"""Intent Normalization application service for AGENTPAY (Phase 144).

Responsibilities:
    - Convert validated StructuredIntent into one canonical deterministic form
    - Normalize action names, intent categories, casing, and currency (e.g. 'usd' -> 'USD')
    - Maintain 100% determinism (normalize(intent) == normalize(intent))
    - Preserve financial Decimal precision without binary floating-point conversion
    - MUST NOT invent or infer missing semantic fields
    - Pure representation — MUST NOT execute payments or mutate state
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from app.schemas.agents import ExtractedEntities, StructuredIntent

logger = logging.getLogger("agentpay.agent.intent_normalization.service")

# Action mapping table to canonical action strings
ACTION_MAPPINGS = {
    "pay": "payment",
    "make payment": "payment",
    "send money": "payment",
    "transfer": "payment",
    "refund": "refund",
    "reimburse": "refund",
    "balance": "balance_query",
    "funds": "balance_query",
    "transaction": "transaction_lookup",
    "history": "transaction_lookup",
    "merchant": "merchant_lookup",
    "user": "user_lookup",
    "agent": "agent_operation",
}


class IntentNormalizationService:
    """Application service for normalizing Structured Intents (Phase 144)."""

    def normalize_intent(
        self,
        intent: StructuredIntent,
        intent_category: str,
    ) -> StructuredIntent:
        """Deterministically normalize StructuredIntent payload into canonical representation."""
        # 1. Normalize Action String
        raw_action = (intent.action or "").lower().strip()
        normalized_action = ACTION_MAPPINGS.get(raw_action, raw_action)

        # 2. Normalize Extracted Entities
        entities = intent.entities
        normalized_amount: Decimal | None = None
        if entities.amount is not None:
            # Preserve Decimal scale cleanly
            normalized_amount = Decimal(str(entities.amount))

        normalized_currency: str | None = None
        if entities.currency:
            normalized_currency = entities.currency.upper().strip()

        normalized_merchant: str | None = None
        if entities.merchant:
            normalized_merchant = entities.merchant.strip()

        normalized_target_id: str | None = None
        if entities.target_id:
            normalized_target_id = entities.target_id.strip()

        normalized_recipient: str | None = None
        if entities.recipient:
            normalized_recipient = entities.recipient.strip()

        # Normalize custom entity keys
        normalized_custom_entities: dict[str, str] = {}
        if entities.custom_entities:
            for k, v in sorted(entities.custom_entities.items()):
                normalized_custom_entities[k.lower().strip()] = str(v).strip()

        normalized_entities = ExtractedEntities(
            amount=normalized_amount,
            currency=normalized_currency,
            merchant=normalized_merchant,
            target_id=normalized_target_id,
            recipient=normalized_recipient,
            custom_entities=normalized_custom_entities,
        )

        # 3. Normalize Parameters and Constraints Keys
        normalized_parameters: dict[str, Any] = {}
        if intent.parameters:
            for k, v in sorted(intent.parameters.items()):
                normalized_parameters[k.lower().strip()] = v

        normalized_constraints: dict[str, Any] = {}
        if intent.constraints:
            for k, v in sorted(intent.constraints.items()):
                normalized_constraints[k.lower().strip()] = v

        # 4. Construct Normalized StructuredIntent
        normalized_intent = StructuredIntent(
            intent_id=intent.intent_id,
            action=normalized_action,
            target=intent.target.strip() if intent.target else None,
            entities=normalized_entities,
            parameters=normalized_parameters,
            constraints=normalized_constraints,
            confidence=intent.confidence.quantize(Decimal("0.0001")),
            source=intent.source.strip() if intent.source else "normalized_provider",
            extracted_at=intent.extracted_at,
        )

        logger.debug(
            "Intent normalized successfully",
            extra={
                "intent_id": str(intent.intent_id),
                "normalized_action": normalized_action,
                "normalized_currency": normalized_currency,
            },
        )

        return normalized_intent
