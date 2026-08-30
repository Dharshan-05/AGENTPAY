"""Agent Planning Engine application service for AGENTPAY (Phase 146).

Responsibilities:
    - Coordinate planning pipeline: Intent -> Plan Generation -> Plan Validation -> Plan Storage
    - Reuses `PurchasePlan` model (`purchase_plans` table) for production plan persistence
    - Enforce tenant isolation (`tenant_id`) and agent boundary (`agent_id`)
    - Audit event emission (`plan_generated`, `plan_validated`, `plan_validation_failed`)
    - Security event emission (`malicious_plan_attempt`) on forbidden secret injection
    - Keyset-paginated listing and IDOR-protected lookup
    - PURE PLANNING REPRESENTATION ONLY: MUST NOT execute plans, call tools, or charge money
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.application.services.intent_normalization_service import IntentNormalizationService
from app.application.services.intent_storage_service import IntentStorageService
from app.application.services.intent_validation_service import IntentValidationService
from app.application.services.plan_generation_service import PlanGenerationService
from app.application.services.plan_validation_service import PlanValidationService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    PlanGenerationError,
    PlanNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.merchant import Merchant
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.purchase_plan import PurchasePlan
from app.schemas.agents import ExtractedEntities, StructuredIntent
from app.schemas.plans import (
    AgentPlan,
    PlanConstraints,
    PlanMetadata,
    PlanStep,
    PlanValidationResult,
)

logger = logging.getLogger("agentpay.agent.planning.service")


class AgentPlanningService:
    """Application service orchestrating Agent Planning Engine (Phase 146)."""

    def __init__(
        self,
        generation_service: PlanGenerationService | None = None,
        validation_service: PlanValidationService | None = None,
        intent_storage_service: IntentStorageService | None = None,
        intent_validation_service: IntentValidationService | None = None,
        intent_normalization_service: IntentNormalizationService | None = None,
        audit_service: AgentAuditService | None = None,
        security_event_service: AgentSecurityEventService | None = None,
    ) -> None:
        self.generation_service = generation_service or PlanGenerationService()
        self.validation_service = validation_service or PlanValidationService()
        self.intent_storage_service = intent_storage_service or IntentStorageService()
        self.intent_validation_service = intent_validation_service or IntentValidationService()
        self.intent_normalization_service = (
            intent_normalization_service or IntentNormalizationService()
        )
        self.audit_service = audit_service or AgentAuditService()
        self.security_event_service = security_event_service or AgentSecurityEventService()

    async def _get_or_create_system_merchant_and_product(
        self, db: AsyncSession, tenant_id: uuid.UUID
    ) -> tuple[uuid.UUID, uuid.UUID]:
        """Helper to ensure valid FK references for PurchasePlan model."""
        m_stmt = select(Merchant).where(
            Merchant.tenant_id == tenant_id, Merchant.deleted_at.is_(None)
        )
        m_res = await db.execute(m_stmt)
        merchant = m_res.scalars().first()

        if merchant is None:
            merchant = Merchant(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                name="System Default Merchant",
                slug=f"system-merchant-{tenant_id.hex[:6]}",
                status="active",
            )
            db.add(merchant)
            await db.flush()

        p_stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.merchant_id == merchant.id,
            Product.deleted_at.is_(None),
        )
        p_res = await db.execute(p_stmt)
        product = p_res.scalars().first()

        if product is None:
            product = Product(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                merchant_id=merchant.id,
                name="System Default Product",
                sku=f"SYS-PROD-{uuid.uuid4().hex[:6]}",
                price=Decimal("0.00"),
                currency_code="USD",
                status="active",
            )
            db.add(product)
            await db.flush()

        return merchant.id, product.id

    async def create_and_validate_plan(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        intent_id: uuid.UUID | None = None,
        request_text: str | None = None,
        context_metadata: dict[str, Any] | None = None,
    ) -> tuple[AgentPlan, PlanValidationResult]:
        """Orchestrate plan generation and validation from intent or request text.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            PlanGenerationError / PlanValidationError: on planning failure.
        """
        # 1. IDOR & Lifecycle Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        if agent.status in ("revoked", "suspended", "deactivated"):
            raise PlanGenerationError(
                f"Agent {agent_id} is '{agent.status}' and cannot generate plans."
            )

        target_intent: StructuredIntent | None = None
        target_category = "UNKNOWN"
        actual_intent_id = intent_id

        # 2. Intent Resolution
        if intent_id:
            stored_intent = await self.intent_storage_service.get_intent(
                db, tenant_id, agent_id, intent_id
            )
            meta = stored_intent.intent_metadata or {}
            norm_payload = meta.get("normalized_payload", {})
            target_category = str(meta.get("intent_type", "UNKNOWN"))
            target_intent = StructuredIntent(
                intent_id=intent_id,
                action=str(norm_payload.get("action", "unknown")),
                confidence=Decimal(str(meta.get("confidence", "1.0"))),
                source="rule_based",
                entities=ExtractedEntities(**norm_payload.get("entities", {})),
            )
        elif request_text:
            stored_intent = await self.intent_storage_service.process_and_store_intent(
                db, tenant_id, agent_id, user_id, request_text, context_metadata
            )
            actual_intent_id = stored_intent.id
            meta = stored_intent.intent_metadata or {}
            norm_payload = meta.get("normalized_payload", {})
            target_category = str(meta.get("intent_type", "UNKNOWN"))
            target_intent = StructuredIntent(
                intent_id=stored_intent.id,
                action=str(norm_payload.get("action", "unknown")),
                confidence=Decimal(str(meta.get("confidence", "1.0"))),
                source="rule_based",
                entities=ExtractedEntities(**norm_payload.get("entities", {})),
            )
        else:
            raise PlanGenerationError("Either intent_id or request_text must be provided.")

        # 3. Phase 147 — Plan Generation
        plan = self.generation_service.generate_plan(
            tenant_id=tenant_id,
            agent_id=agent_id,
            intent=target_intent,
            intent_category=target_category,
            intent_id=actual_intent_id,
            context_metadata=context_metadata,
        )

        # 4. Phase 148 — Plan Validation
        val_result = self.validation_service.validate_plan(
            plan=plan, target_tenant_id=tenant_id, target_agent_id=agent_id
        )

        # 5. Secret Injection Security Event Check
        if any("Secret material detected" in err for err in val_result.errors):
            await self.security_event_service.record_security_event(
                db,
                tenant_id=tenant_id,
                agent_id=agent_id,
                event_type="malicious_plan_attempt",
                event_action="validate_plan",
                event_result="denied",
                severity="high",
                event_payload={"plan_id": str(plan.plan_id), "errors": val_result.errors},
            )

        # 6. Reusing PurchasePlan model for Persistence
        merchant_id, product_id = await self._get_or_create_system_merchant_and_product(
            db, tenant_id
        )
        plan_amount = plan.constraints.max_amount or Decimal("0.0000")
        currency = (
            plan.constraints.allowed_currencies[0] if plan.constraints.allowed_currencies else "USD"
        )

        db_plan = PurchasePlan(
            id=plan.plan_id,
            tenant_id=tenant_id,
            purchase_intent_id=actual_intent_id or plan.plan_id,
            merchant_id=merchant_id,
            agent_id=agent_id,
            product_id=product_id,
            plan_reference=f"plan-{plan.plan_id.hex[:12]}",
            status="ready" if val_result.is_valid and val_result.execution_eligible else "draft",
            quantity=Decimal("1.000"),
            unit_price=plan_amount,
            subtotal=plan_amount,
            total_amount=plan_amount,
            currency_code=currency,
            plan_metadata={
                "intent_type": target_category,
                "version": plan.version,
                "steps": [s.model_dump(mode="json") for s in plan.steps],
                "constraints": plan.constraints.model_dump(mode="json"),
                "metadata": plan.metadata.model_dump(mode="json"),
                "validation": val_result.model_dump(mode="json"),
            },
        )
        db.add(db_plan)

        # 7. Audit Event Registration
        audit_event = "plan_validated" if val_result.is_valid else "plan_validation_failed"
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type=audit_event,
            event_action="generate_and_validate_plan",
            event_result="success" if val_result.is_valid else "failure",
            event_metadata={
                "plan_id": str(plan.plan_id),
                "intent_type": target_category,
                "is_valid": val_result.is_valid,
                "execution_eligible": val_result.execution_eligible,
                "error_count": len(val_result.errors),
            },
        )

        await db.commit()
        await db.refresh(db_plan)

        logger.info(
            "Agent plan created and validated",
            extra={
                "plan_id": str(plan.plan_id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "is_valid": val_result.is_valid,
            },
        )

        return plan, val_result

    async def get_plan(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        plan_id: uuid.UUID,
    ) -> AgentPlan:
        """Retrieve stored plan representation by ID within verified tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            PlanNotFoundError: if plan is missing.
        """
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        plan_stmt = select(PurchasePlan).where(
            PurchasePlan.id == plan_id,
            PurchasePlan.agent_id == agent_id,
            PurchasePlan.tenant_id == tenant_id,
            PurchasePlan.deleted_at.is_(None),
        )
        plan_res = await db.execute(plan_stmt)
        db_plan = plan_res.scalar_one_or_none()
        if db_plan is None:
            raise PlanNotFoundError(f"Plan {plan_id} not found.")

        meta = db_plan.plan_metadata or {}
        return AgentPlan(
            plan_id=db_plan.id,
            tenant_id=db_plan.tenant_id,
            agent_id=db_plan.agent_id,
            intent_id=db_plan.purchase_intent_id,
            intent_type=str(meta.get("intent_type", "UNKNOWN")),
            version=str(meta.get("version", "1.0.0")),
            status=db_plan.status,
            steps=[PlanStep(**s) for s in meta.get("steps", [])],
            constraints=PlanConstraints(**meta.get("constraints", {})),
            metadata=PlanMetadata(**meta.get("metadata", {})),
            created_at=db_plan.created_at,
        )

    async def validate_existing_plan(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        plan: AgentPlan,
    ) -> PlanValidationResult:
        """Validate an input AgentPlan representation against tenant/agent boundaries."""
        val_res = self.validation_service.validate_plan(
            plan=plan, target_tenant_id=tenant_id, target_agent_id=agent_id
        )
        return val_res
