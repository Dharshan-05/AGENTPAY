"""Intent Storage application service for AGENTPAY (Phase 145).

Responsibilities:
    - Process pipeline: Extraction -> Classification -> Validation -> Normalization -> Storage
    - Persist normalized intent by reusing the production `PurchaseIntent` model
    - Enforce strict tenant isolation (`tenant_id`) and agent boundary (`agent_id`)
    - Verify agent lifecycle status (deactivated/suspended agents cannot store intents)
    - Transaction safety: Atomic database commit
    - Audit integration: Record `intent_stored` audit events with sanitized metadata
    - Read capabilities: Keyset-paginated listing and IDOR-protected lookup
    - PURE PERSISTENCE ONLY: MUST NOT execute payments, call tools, plan, or execute
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.intent_classification_service import IntentClassificationService
from app.application.services.intent_extraction_service import IntentExtractionService
from app.application.services.intent_normalization_service import IntentNormalizationService
from app.application.services.intent_validation_service import IntentValidationService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    IntentNotFoundError,
    IntentValidationError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.merchant import Merchant
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.purchase_intent import PurchaseIntent

logger = logging.getLogger("agentpay.agent.intent_storage.service")

# Secret redaction pattern for raw request text storage
SECRET_REDACT_PATTERN = re.compile(
    r"(?i)(password|secret|bearer\s+[a-z0-9\-\._~\+\/]+=*|api_key|private_key|token)[:=]\s*([^\s,]+)"  # noqa: E501
)


class IntentStorageService:
    """Application service orchestrating Intent Storage (Phase 145)."""

    def __init__(
        self,
        extraction_service: IntentExtractionService | None = None,
        classification_service: IntentClassificationService | None = None,
        validation_service: IntentValidationService | None = None,
        normalization_service: IntentNormalizationService | None = None,
        audit_service: AgentAuditService | None = None,
    ) -> None:
        self.extraction_service = extraction_service or IntentExtractionService()
        self.classification_service = classification_service or IntentClassificationService()
        self.validation_service = validation_service or IntentValidationService()
        self.normalization_service = normalization_service or IntentNormalizationService()
        self.audit_service = audit_service or AgentAuditService()

    async def _get_or_create_system_merchant_and_product(
        self, db: AsyncSession, tenant_id: uuid.UUID
    ) -> tuple[uuid.UUID, uuid.UUID]:
        """Helper to ensure valid FK references for PurchaseIntent model."""
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

    async def process_and_store_intent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        request_text: str,
        context_metadata: dict[str, Any] | None = None,
    ) -> PurchaseIntent:
        """Process intent pipeline and persist normalized result inside tenant transaction.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            IntentValidationError: if intent validation fails.
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
            raise IntentValidationError(
                f"Agent {agent_id} is '{agent.status}' and cannot store operational intents."
            )

        meta = context_metadata or {}

        # 2. Phase 140 — Extraction
        ext_res = await self.extraction_service.extract_intent(
            db, tenant_id, agent_id, request_text, meta
        )

        # 3. Phase 141 — Classification
        class_res = await self.classification_service.classify_intent(
            db, tenant_id, agent_id, ext_res.extracted_intent
        )
        intent_cat = class_res.classification.intent_category

        # 4. Phase 143 — Validation
        val_res = await self.validation_service.validate_intent(
            db, tenant_id, agent_id, ext_res.extracted_intent, intent_cat
        )
        if not val_res.is_valid:
            raise IntentValidationError(
                f"Intent validation failed: {'; '.join(val_res.validation_errors)}"
            )

        # 5. Phase 144 — Normalization
        norm_intent = self.normalization_service.normalize_intent(
            ext_res.extracted_intent, intent_cat
        )

        # 6. Phase 145 — Storage (Reusing PurchaseIntent model)
        sanitized_text = SECRET_REDACT_PATTERN.sub(r"\1=[REDACTED]", request_text)
        merchant_id, product_id = await self._get_or_create_system_merchant_and_product(
            db, tenant_id
        )

        intent_amount = norm_intent.entities.amount or Decimal("0.0000")
        currency = norm_intent.entities.currency or "USD"

        stored_intent = PurchaseIntent(
            id=norm_intent.intent_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            merchant_id=merchant_id,
            product_id=product_id,
            intent_reference=f"intent-{norm_intent.intent_id.hex[:12]}",
            status="pending",
            quantity=Decimal("1.000"),
            unit_price=intent_amount,
            total_amount=intent_amount,
            currency_code=currency,
            actor_id=user_id,
            actor_type="user",
            intent_metadata={
                "intent_type": intent_cat,
                "status": "stored",
                "confidence": str(norm_intent.confidence),
                "raw_text": sanitized_text,
                "normalized_payload": norm_intent.model_dump(mode="json"),
                "validation_metadata": val_res.model_dump(mode="json"),
            },
        )
        db.add(stored_intent)

        # 7. Audit Event Registration
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="intent_stored",
            event_action="store_intent",
            event_result="success",
            event_metadata={
                "intent_id": str(norm_intent.intent_id),
                "intent_type": intent_cat,
                "confidence": str(norm_intent.confidence),
                "is_execution_eligible": val_res.is_execution_eligible,
            },
        )

        await db.commit()
        await db.refresh(stored_intent)

        logger.info(
            "Agent intent stored successfully",
            extra={
                "intent_id": str(stored_intent.id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "intent_type": intent_cat,
            },
        )

        return stored_intent

    async def get_intent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        intent_id: uuid.UUID,
    ) -> PurchaseIntent:
        """Retrieve stored intent by ID within verified tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            IntentNotFoundError: if intent is missing.
        """
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        intent_stmt = select(PurchaseIntent).where(
            PurchaseIntent.id == intent_id,
            PurchaseIntent.agent_id == agent_id,
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.deleted_at.is_(None),
        )
        intent_res = await db.execute(intent_stmt)
        stored_intent = intent_res.scalar_one_or_none()
        if stored_intent is None:
            raise IntentNotFoundError(f"Stored intent {intent_id} not found.")

        return stored_intent

    async def list_intents(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = 20,
    ) -> tuple[list[PurchaseIntent], bool]:
        """List stored intents using keyset pagination."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        query = select(PurchaseIntent).where(
            PurchaseIntent.agent_id == agent_id,
            PurchaseIntent.tenant_id == tenant_id,
            PurchaseIntent.deleted_at.is_(None),
        )

        if cursor_created_at and cursor_id:
            query = query.where(
                or_(
                    PurchaseIntent.created_at < cursor_created_at,
                    and_(
                        PurchaseIntent.created_at == cursor_created_at,
                        PurchaseIntent.id < cursor_id,
                    ),
                )
            )

        query = query.order_by(PurchaseIntent.created_at.desc(), PurchaseIntent.id.desc()).limit(
            limit + 1
        )

        result = await db.execute(query)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]

        return items, has_more
