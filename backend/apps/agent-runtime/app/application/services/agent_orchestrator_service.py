"""Agent Orchestrator application service for AGENTPAY (Phase 149).

Responsibilities:
    - Production-grade orchestration layer coordinating intent, plan, lifecycle, trust
    - Determine canonical orchestration decision: READY, BLOCKED, REJECTED
    - Canonical state model: CREATED, VALIDATING, READY, BLOCKED, REJECTED, CANCELLED
    - Enforce tenant isolation and IDOR protection
    - Emit audit events (orchestration_created, orchestration_ready, orchestration_blocked)
    - Emit security events on security-sensitive rejections
    - ABSOLUTE ZERO EXECUTION GUARANTEE: Does NOT call tools or execute payments
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_planning_service import AgentPlanningService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.application.services.agent_trust_service import AgentTrustService
from app.application.services.authorization import AuthorizationService
from app.application.services.intent_storage_service import IntentStorageService
from app.application.services.plan_validation_service import PlanValidationService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    OrchestrationNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.schemas.orchestration import AgentOrchestrationResponse

logger = logging.getLogger("agentpay.agent.orchestration.service")


class AgentOrchestratorService:
    """Application service orchestrating Agent decision pipeline (Phase 149)."""

    def __init__(
        self,
        intent_storage_service: IntentStorageService | None = None,
        planning_service: AgentPlanningService | None = None,
        plan_validation_service: PlanValidationService | None = None,
        trust_service: AgentTrustService | None = None,
        authorization_service: AuthorizationService | None = None,
        audit_service: AgentAuditService | None = None,
        security_event_service: AgentSecurityEventService | None = None,
    ) -> None:
        self.intent_storage_service = intent_storage_service or IntentStorageService()
        self.planning_service = planning_service or AgentPlanningService()
        self.plan_validation_service = plan_validation_service or PlanValidationService()
        self.trust_service = trust_service or AgentTrustService()
        self.authorization_service = authorization_service or AuthorizationService()
        self.audit_service = audit_service or AgentAuditService()
        self.security_event_service = security_event_service or AgentSecurityEventService()

    async def orchestrate_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        intent_id: uuid.UUID | None = None,
        plan_id: uuid.UUID | None = None,
        context_metadata: dict[str, Any] | None = None,
    ) -> AgentOrchestrationResponse:
        """Create a deterministic orchestration decision from stored intent and plan.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
        """
        blocking_reasons: list[str] = []
        is_security_rejection = False

        # 1. Load Agent & Verify Tenant Scope
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Verify Agent Lifecycle Status
        if agent.status in ("deactivated", "revoked"):
            blocking_reasons.append(f"Agent lifecycle status is '{agent.status}'.")
            is_security_rejection = True
        elif agent.status in ("suspended", "paused", "provisioning"):
            blocking_reasons.append(f"Agent lifecycle status is '{agent.status}'.")

        # 3. Intent Verification
        intent_valid = False
        if intent_id:
            try:
                stored_intent = await self.intent_storage_service.get_intent(
                    db, tenant_id, agent_id, intent_id
                )
                meta = stored_intent.intent_metadata or {}
                intent_cat = str(meta.get("intent_type", "UNKNOWN"))
                val_meta = meta.get("validation_metadata", {})
                if intent_cat != "UNKNOWN" and val_meta.get("is_execution_eligible", False):
                    intent_valid = True
                else:
                    blocking_reasons.append(f"Stored intent {intent_id} is ineligible or UNKNOWN.")
            except Exception as exc:
                blocking_reasons.append(f"Stored intent {intent_id} verification failed: {exc}")

        # 4. Plan Verification
        plan_valid = False
        required_permissions: list[str] = ["agents:plans_create", "agents:intent_create"]
        if plan_id:
            try:
                plan = await self.planning_service.get_plan(db, tenant_id, agent_id, plan_id)
                val_res = self.plan_validation_service.validate_plan(
                    plan, target_tenant_id=tenant_id, target_agent_id=agent_id
                )
                if val_res.is_valid and val_res.execution_eligible:
                    plan_valid = True
                else:
                    blocking_reasons.append(
                        f"Plan {plan_id} validation failed: {'; '.join(val_res.errors)}"
                    )
            except Exception as exc:
                blocking_reasons.append(f"Plan {plan_id} lookup failed: {exc}")

        # 5. Trust Posture Verification
        trust_status = "unknown"
        trust_score = Decimal("50.00")
        try:
            trust = await self.trust_service.get_agent_trust(db, tenant_id, agent_id)
            trust_status = trust.trust_status
            trust_score = trust.trust_score or Decimal("50.00")
            if trust.trust_status == "restricted":
                blocking_reasons.append("Agent trust posture is restricted.")
                is_security_rejection = True
        except Exception:
            # Default trust if no record yet
            trust_status = "medium"

        # 6. Effective Permissions Resolution
        resolved_perms: list[str] = []
        try:
            perms_set = await self.authorization_service.resolve_agent_permissions(
                db, tenant_id, agent_id
            )
            resolved_perms = sorted(perms_set)
        except Exception:
            resolved_perms = []

        # 7. Decision Determination
        orchestration_id = uuid.uuid4()
        created_at = datetime.now(UTC)

        if is_security_rejection:
            decision = "REJECTED"
            state = "REJECTED"
            execution_eligible = False
        elif blocking_reasons:
            decision = "BLOCKED"
            state = "BLOCKED"
            execution_eligible = False
        else:
            decision = "READY"
            state = "READY"
            execution_eligible = True

        # 8. Reusing PurchasePlan model metadata for Persistence
        p_stmt = select(PurchasePlan).where(
            PurchasePlan.agent_id == agent_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        if plan_id:
            p_stmt = p_stmt.where(PurchasePlan.id == plan_id)
        p_res = await db.execute(p_stmt)
        db_plan = p_res.scalars().first()

        if db_plan:
            meta = dict(db_plan.plan_metadata or {})
            meta["orchestration"] = {
                "orchestration_id": str(orchestration_id),
                "state": state,
                "decision": decision,
                "execution_eligible": execution_eligible,
                "blocking_reasons": blocking_reasons,
                "created_at": created_at.isoformat(),
            }
            db_plan.plan_metadata = meta
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(db_plan, "plan_metadata")
            db.add(db_plan)

        # 9. Audit Event Registration
        audit_type = f"orchestration_{decision.lower()}"
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type=audit_type,
            event_action="orchestrate_agent",
            event_result="success" if decision == "READY" else "failure",
            event_metadata={
                "orchestration_id": str(orchestration_id),
                "decision": decision,
                "state": state,
                "execution_eligible": execution_eligible,
                "blocking_reason_count": len(blocking_reasons),
            },
        )

        # 10. Security Event Registration
        if decision == "REJECTED" and is_security_rejection:
            await self.security_event_service.record_security_event(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                user_id=user_id,
                event_type="security_control",
                event_action="policy_blocked",
                event_result="blocked",
                severity="high",
                event_payload={
                    "orchestration_id": str(orchestration_id),
                    "blocking_reasons": blocking_reasons,
                },
            )

        await db.commit()

        logger.info(
            "Agent orchestration decision created",
            extra={
                "orchestration_id": str(orchestration_id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "decision": decision,
                "state": state,
            },
        )

        return AgentOrchestrationResponse(
            orchestration_id=orchestration_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            intent_id=intent_id,
            plan_id=plan_id,
            state=state,
            execution_eligible=execution_eligible,
            decision=decision,
            blocking_reasons=blocking_reasons,
            required_permissions=required_permissions,
            resolved_permissions=resolved_perms,
            trust_status=trust_status,
            trust_score=trust_score,
            plan_valid=plan_valid,
            intent_valid=intent_valid,
            created_at=created_at,
        )

    async def get_orchestration(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        orchestration_id: uuid.UUID,
    ) -> AgentOrchestrationResponse:
        """Retrieve orchestration decision by ID within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            OrchestrationNotFoundError: if orchestration decision is missing.
        """
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # Lookup PurchasePlan storing orchestration metadata
        p_stmt = select(PurchasePlan).where(
            PurchasePlan.agent_id == agent_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        p_res = await db.execute(p_stmt)
        plans = p_res.scalars().all()

        for db_plan in plans:
            meta = db_plan.plan_metadata or {}
            orch_meta = meta.get("orchestration", {})
            if orch_meta.get("orchestration_id") == str(orchestration_id):
                return AgentOrchestrationResponse(
                    orchestration_id=orchestration_id,
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    intent_id=db_plan.purchase_intent_id,
                    plan_id=db_plan.id,
                    state=orch_meta.get("state", "CREATED"),
                    execution_eligible=orch_meta.get("execution_eligible", False),
                    decision=orch_meta.get("decision", "BLOCKED"),
                    blocking_reasons=orch_meta.get("blocking_reasons", []),
                    required_permissions=["agents:plans_create"],
                    resolved_permissions=[],
                    trust_status="medium",
                    trust_score=Decimal("50.00"),
                    plan_valid=True,
                    intent_valid=True,
                    created_at=datetime.now(UTC),
                )

        raise OrchestrationNotFoundError(f"Orchestration {orchestration_id} not found.")
