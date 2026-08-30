"""Intent Classification & Structured Intent application service for AGENTPAY (Phase 141 & 142).

Responsibilities:
    - Map extracted semantic intent (`StructuredIntent`) into canonical category
    - Canonical taxonomy: PAYMENT, REFUND, TRANSACTION_LOOKUP, BALANCE_QUERY, MERCHANT_LOOKUP, etc.
    - Bounded classification confidence (0.00 <= confidence <= 1.00)
    - Produce server-controlled `StructuredIntentResponse` contract
    - CLASSIFICATION & REPRESENTATION ONLY: MUST NOT execute payments or mutate state
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.schemas.agents import (
    IntentClassificationResponse,
    StructuredIntent,
    StructuredIntentResponse,
)

logger = logging.getLogger("agentpay.agent.intent_classification.service")

# Centralized canonical classification taxonomy
CANONICAL_INTENT_CATEGORIES = frozenset(
    {
        "PAYMENT",
        "REFUND",
        "TRANSACTION_LOOKUP",
        "BALANCE_QUERY",
        "MERCHANT_LOOKUP",
        "USER_LOOKUP",
        "AGENT_OPERATION",
        "UNKNOWN",
    }
)


class IntentClassificationService:
    """Application service for intent classification (Phase 141 & Phase 142)."""

    async def classify_intent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        intent: StructuredIntent,
    ) -> StructuredIntentResponse:
        """Classify extracted intent and return server-populated StructuredIntentResponse.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            IntentClassificationError: if classification fails.
        """
        # 1. IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        now = datetime.now(UTC)
        action = (intent.action or "").lower().strip()

        # 2. Deterministic Classification Taxonomy Mapping
        category = "UNKNOWN"
        confidence = intent.confidence
        reason = "Extracted action mapped to canonical classification category."

        if action in ("payment", "pay", "transfer"):
            category = "PAYMENT"
        elif action in ("refund", "reimburse"):
            category = "REFUND"
        elif action in ("transaction_lookup", "history", "lookup_transaction"):
            category = "TRANSACTION_LOOKUP"
        elif action in ("balance_query", "balance", "funds"):
            category = "BALANCE_QUERY"
        elif action in ("merchant_lookup", "merchant"):
            category = "MERCHANT_LOOKUP"
        elif action in ("user_lookup", "user"):
            category = "USER_LOOKUP"
        elif action in ("agent_operation", "status", "pause", "resume"):
            category = "AGENT_OPERATION"
        else:
            category = "UNKNOWN"
            confidence = Decimal("0.00")
            reason = f"Unrecognized action '{action}' classified as UNKNOWN."

        # Ambiguity check: Low extraction confidence forces UNKNOWN
        if intent.confidence < Decimal("0.50"):
            category = "UNKNOWN"
            confidence = intent.confidence
            reason = f"Low confidence ({intent.confidence:.2f}) forces UNKNOWN classification."

        # Ensure confidence is strictly bounded [0.00, 1.00]
        confidence = min(Decimal("1.00"), max(Decimal("0.00"), confidence))

        classification = IntentClassificationResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            intent_category=category,
            confidence=confidence.quantize(Decimal("0.01")),
            reason=reason,
            classified_at=now,
        )

        logger.info(
            "Intent classified",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "intent_category": category,
                "confidence": str(confidence),
            },
        )

        return StructuredIntentResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            intent=intent,
            classification=classification,
        )
