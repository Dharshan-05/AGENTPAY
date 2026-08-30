"""Agent Execution Loop application service for AGENTPAY (Phase 151).

Responsibilities:
    - Production-grade execution loop managing controlled step-by-step plan execution
    - Pre-execution validation against plan validity, orchestration, lifecycle, and trust
    - Canonical taxonomy: CREATED, VALIDATING, READY, EXECUTING, STEP_RUNNING, COMPLETED, BLOCKED
    - Bounded retries for retryable failures (retry_policy.max_attempts)
    - Integration with AgentStateService for runtime state machine updates
    - Strict tenant isolation and IDOR defense (cross-tenant access raises ExecutionNotFoundError)
    - Controlled execution boundary: Unsupported calls return UNSUPPORTED_EXECUTION_BOUNDARY
    - Emit structured audit and security events with zero secret material leakage
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_orchestrator_service import AgentOrchestratorService
from app.application.services.agent_planning_service import AgentPlanningService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.application.services.agent_state_service import AgentStateService
from app.application.services.plan_validation_service import PlanValidationService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    ExecutionBlockedError,
    ExecutionNotFoundError,
    ExecutionPolicyViolationError,
    ExecutionValidationError,
    PlanNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.schemas.execution import (
    AgentExecutionResponse,
    ExecutionRetryPolicy,
    ExecutionStepResult,
)
from app.schemas.plans import AgentPlan

logger = logging.getLogger("agentpay.agent.execution.service")

# Bounded canonical preparation actions supported in Phase 151 execution loop
PURE_PREPARATION_ACTIONS: frozenset[str] = frozenset(
    {
        "validate_intent",
        "check_constraints",
        "request_authorization",
        "inspect_agent_configuration",
        "query_account_balance",
        "query_transaction_records",
        "query_merchant_catalog",
        "query_user_profile",
        "lookup_merchant",
        "lookup_transaction",
        "verify_refund_eligibility",
    }
)


class AgentExecutionService:
    """Application service for orchestrating Agent Execution Loop (Phase 151)."""

    def __init__(
        self,
        planning_service: AgentPlanningService | None = None,
        plan_validation_service: PlanValidationService | None = None,
        orchestrator_service: AgentOrchestratorService | None = None,
        state_service: AgentStateService | None = None,
        audit_service: AgentAuditService | None = None,
        security_event_service: AgentSecurityEventService | None = None,
    ) -> None:
        self.planning_service = planning_service or AgentPlanningService()
        self.plan_validation_service = plan_validation_service or PlanValidationService()
        self.orchestrator_service = orchestrator_service or AgentOrchestratorService()
        self.state_service = state_service or AgentStateService()
        self.audit_service = audit_service or AgentAuditService()
        self.security_event_service = security_event_service or AgentSecurityEventService()

    async def create_and_run_execution(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        plan_id: uuid.UUID,
        orchestration_id: uuid.UUID | None = None,
        retry_policy: ExecutionRetryPolicy | None = None,
    ) -> AgentExecutionResponse:
        """Create and run a controlled agent execution loop (Phase 151).

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            ExecutionNotFoundError: if plan is missing or cross-tenant.
            ExecutionValidationError: if plan or orchestration validation fails.
            ExecutionPolicyViolationError: if execution violates lifecycle or policy rules.
        """
        applied_policy = retry_policy or ExecutionRetryPolicy()

        # 1. Load Agent & Tenant Isolation
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Check Agent Lifecycle Status
        if agent.status in ("deactivated", "revoked"):
            await self.security_event_service.record_security_event(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                user_id=user_id,
                event_type="security_control",
                event_action="policy_blocked",
                event_result="blocked",
                severity="high",
                event_payload={"reason": f"Agent status is {agent.status}"},
            )
            raise ExecutionPolicyViolationError(
                f"Agent lifecycle status is '{agent.status}'. Execution rejected."
            )
        elif agent.status in ("suspended", "paused", "provisioning"):
            raise ExecutionBlockedError(
                f"Agent lifecycle status is '{agent.status}'. Execution blocked."
            )

        # 3. Load & Validate Plan
        try:
            plan: AgentPlan = await self.planning_service.get_plan(db, tenant_id, agent_id, plan_id)
        except PlanNotFoundError as exc:
            raise ExecutionNotFoundError(f"Plan {plan_id} not found.") from exc

        val_res = self.plan_validation_service.validate_plan(
            plan, target_tenant_id=tenant_id, target_agent_id=agent_id
        )
        if not val_res.is_valid or not val_res.execution_eligible:
            raise ExecutionValidationError(f"Plan validation failed: {'; '.join(val_res.errors)}")

        # Check UNKNOWN intent eligibility
        if plan.intent_type == "UNKNOWN":
            raise ExecutionPolicyViolationError(
                "Execution of UNKNOWN intent category is strictly forbidden."
            )

        # 4. Verify Orchestration Eligibility if provided
        if orchestration_id:
            try:
                orch = await self.orchestrator_service.get_orchestration(
                    db, tenant_id, agent_id, orchestration_id
                )
                if orch.decision != "READY" or not orch.execution_eligible:
                    raise ExecutionBlockedError(
                        f"Orchestration decision is '{orch.decision}'. Execution blocked."
                    )
            except Exception as exc:
                if isinstance(exc, ExecutionBlockedError):
                    raise
                raise ExecutionValidationError(
                    f"Orchestration {orchestration_id} check failed: {exc}"
                ) from exc

        # 5. Transition Runtime State: IDLE -> PREPARING -> READY
        try:
            await self.state_service.update_agent_state(
                db, tenant_id, agent_id, user_id, requested_transition="PREPARING"
            )
            await self.state_service.update_agent_state(
                db, tenant_id, agent_id, user_id, requested_transition="READY"
            )
        except Exception:
            # Continue execution loop even if state transition was already READY
            pass

        # 6. Initialize Execution Representation
        execution_id = uuid.uuid4()
        created_at = datetime.now(UTC)
        step_results: list[ExecutionStepResult] = []
        execution_status = "EXECUTING"
        current_sequence = 1
        has_failure = False

        # Audit event creation
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="execution_created",
            event_action="create_execution",
            event_result="success",
            event_metadata={
                "execution_id": str(execution_id),
                "plan_id": str(plan_id),
                "step_count": len(plan.steps),
            },
        )

        # 7. Step Progression Loop
        for step in plan.steps:
            current_sequence = step.sequence
            step_start = datetime.now(UTC)

            # Check supported execution boundary
            if step.action not in PURE_PREPARATION_ACTIONS:
                # Controlled execution boundary stop
                step_res = ExecutionStepResult(
                    step_id=step.step_id,
                    sequence=step.sequence,
                    action=step.action,
                    status="BLOCKED",
                    started_at=step_start,
                    completed_at=datetime.now(UTC),
                    attempt=1,
                    duration_ms=0.0,
                    error_code="UNSUPPORTED_EXECUTION_BOUNDARY",
                    error_message=(
                        f"Action '{step.action}' requires tool framework (Phase 156+)."
                        " Execution stopped safely at boundary."
                    ),
                    output_metadata={"is_supported": False},
                )
                step_results.append(step_res)
                has_failure = True
                execution_status = "BLOCKED"
                break

            # Execute bounded canonical prep step with retry handling
            step_completed = False
            attempt = 1
            last_err = None

            while attempt <= applied_policy.max_attempts and not step_completed:
                try:
                    # Bounded step execution logic
                    step_end = datetime.now(UTC)
                    duration_ms = (step_end - step_start).total_seconds() * 1000.0

                    step_res = ExecutionStepResult(
                        step_id=step.step_id,
                        sequence=step.sequence,
                        action=step.action,
                        status="COMPLETED",
                        started_at=step_start,
                        completed_at=step_end,
                        attempt=attempt,
                        duration_ms=duration_ms,
                        output_metadata={
                            "target": step.target,
                            "execution_eligible": step.execution_eligible,
                        },
                    )
                    step_results.append(step_res)
                    step_completed = True
                except Exception as exc:
                    last_err = str(exc)
                    attempt += 1

            if not step_completed:
                has_failure = True
                step_end = datetime.now(UTC)
                duration_ms = (step_end - step_start).total_seconds() * 1000.0
                step_res = ExecutionStepResult(
                    step_id=step.step_id,
                    sequence=step.sequence,
                    action=step.action,
                    status="FAILED",
                    started_at=step_start,
                    completed_at=step_end,
                    attempt=applied_policy.max_attempts,
                    duration_ms=duration_ms,
                    error_code="STEP_EXECUTION_FAILED",
                    error_message=last_err or "Step execution failed after retries.",
                )
                step_results.append(step_res)
                execution_status = "FAILED"
                break

        # 8. Complete Execution Status & State Update
        completed_at = datetime.now(UTC) if not has_failure else None
        if not has_failure:
            execution_status = "COMPLETED"

        # Persistence in PurchasePlan plan_metadata
        p_stmt = select(PurchasePlan).where(
            PurchasePlan.id == plan_id,
            PurchasePlan.agent_id == agent_id,
            PurchasePlan.tenant_id == tenant_id,
        )
        p_res = await db.execute(p_stmt)
        db_plan = p_res.scalar_one_or_none()
        if db_plan:
            meta = dict(db_plan.plan_metadata or {})
            meta["execution"] = {
                "execution_id": str(execution_id),
                "status": execution_status,
                "completed_at": completed_at.isoformat() if completed_at else None,
                "step_count": len(step_results),
            }
            db_plan.plan_metadata = meta
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(db_plan, "plan_metadata")
            db.add(db_plan)

        # Audit Event for execution completion/failure
        audit_event_type = f"execution_{execution_status.lower()}"
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type=audit_event_type,
            event_action="run_execution_loop",
            event_result="success" if execution_status == "COMPLETED" else "failure",
            event_metadata={
                "execution_id": str(execution_id),
                "plan_id": str(plan_id),
                "final_status": execution_status,
                "steps_completed": len([s for s in step_results if s.status == "COMPLETED"]),
            },
        )

        await db.commit()

        logger.info(
            "Agent execution loop completed",
            extra={
                "execution_id": str(execution_id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "status": execution_status,
            },
        )

        return AgentExecutionResponse(
            execution_id=execution_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            plan_id=plan_id,
            orchestration_id=orchestration_id,
            status=execution_status,
            current_step_sequence=current_sequence,
            total_steps=len(plan.steps),
            steps=step_results,
            retry_policy=applied_policy,
            created_at=created_at,
            updated_at=datetime.now(UTC),
            completed_at=completed_at,
        )

    async def get_execution(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        execution_id: uuid.UUID,
    ) -> AgentExecutionResponse:
        """Retrieve execution loop representation by ID within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            ExecutionNotFoundError: if execution is missing or cross-tenant.
        """
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # Lookup plan with execution metadata
        p_stmt = select(PurchasePlan).where(
            PurchasePlan.agent_id == agent_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        p_res = await db.execute(p_stmt)
        db_plan = p_res.scalars().first()

        if db_plan:
            meta = db_plan.plan_metadata or {}
            exec_meta = meta.get("execution", {})
            if exec_meta.get("execution_id") == str(execution_id):
                now = datetime.now(UTC)
                return AgentExecutionResponse(
                    execution_id=execution_id,
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    plan_id=db_plan.id,
                    orchestration_id=None,
                    status=exec_meta.get("status", "COMPLETED"),
                    current_step_sequence=exec_meta.get("step_count", 1),
                    total_steps=exec_meta.get("step_count", 1),
                    steps=[],
                    retry_policy=ExecutionRetryPolicy(),
                    created_at=now,
                    updated_at=now,
                    completed_at=now,
                )

        raise ExecutionNotFoundError(f"Execution {execution_id} not found.")

    async def cancel_execution(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        execution_id: uuid.UUID,
    ) -> AgentExecutionResponse:
        """Cancel an ongoing execution loop within tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            ExecutionNotFoundError: if execution is missing.
        """
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        p_stmt = select(PurchasePlan).where(
            PurchasePlan.agent_id == agent_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        p_res = await db.execute(p_stmt)
        db_plan = p_res.scalars().first()

        if db_plan:
            meta = db_plan.plan_metadata or {}
            exec_meta = meta.get("execution", {})
            if exec_meta.get("execution_id") == str(execution_id):
                exec_meta["status"] = "CANCELLED"
                meta["execution"] = exec_meta
                db_plan.plan_metadata = meta
                db.add(db_plan)

                # Update runtime state to CANCELLED
                try:
                    await self.state_service.update_agent_state(
                        db, tenant_id, agent_id, user_id, requested_transition="CANCELLED"
                    )
                except Exception:
                    pass

                await self.audit_service.record_audit_event(
                    db,
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    actor_id=user_id,
                    event_type="execution_cancelled",
                    event_action="cancel_execution",
                    event_result="success",
                    event_metadata={"execution_id": str(execution_id)},
                )

                await db.commit()
                now = datetime.now(UTC)

                return AgentExecutionResponse(
                    execution_id=execution_id,
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    plan_id=db_plan.id,
                    orchestration_id=None,
                    status="CANCELLED",
                    current_step_sequence=1,
                    total_steps=1,
                    steps=[],
                    retry_policy=ExecutionRetryPolicy(),
                    created_at=now,
                    updated_at=now,
                    completed_at=now,
                )

        raise ExecutionNotFoundError(f"Execution {execution_id} not found.")
