"""Intent Risk Features Pipeline (Phase 226)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.application.services.intent_risk_service import IntentRiskService
from app.ml.features.base import FeatureDefinition, FeatureType, FeatureValue
from app.schemas.intent_risk import IntentRiskRequest

logger = logging.getLogger("fraudguard.ml.features.intent")

DEF_INTENT_RISK_SCORE = FeatureDefinition(
    name="intent_risk_score",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_INTENT_RISK",
    transformation_description="Authoritative AGENTGUARD intent risk score (0.00 to 1.00)",
    version="1.0.0",
)

DEF_INTENT_CAN_PROCEED = FeatureDefinition(
    name="intent_can_proceed",
    feature_type=FeatureType.BOOLEAN,
    source="AGENTGUARD_INTENT_RISK",
    transformation_description="False if critical intent mismatch renders execution unsafe",
    version="1.0.0",
)


class IntentRiskFeatureExtractor:
    """Production Intent Risk Feature Extractor (Phase 226)."""

    def __init__(self, intent_risk_service: IntentRiskService | None = None) -> None:
        self.intent_risk_service = intent_risk_service or IntentRiskService()

    def extract_features(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        record: dict[str, Any],
    ) -> list[FeatureValue]:
        """Extract intent risk ML features consuming AGENTGUARD intent engine (Phase 226)."""
        i_req = IntentRiskRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            declared_intent=record.get("declared_intent"),
            requested_action=record.get("requested_action", "payment"),
            requested_amount=record.get("amount"),
            requested_currency=record.get("currency", "USD"),
            requested_merchant_id=(
                str(record["merchant_id"]) if record.get("merchant_id") else None
            ),
            requested_category=record.get("category"),
        )
        i_res = self.intent_risk_service.calculate_intent_risk(i_req)

        t_str = str(tenant_id)
        a_str = str(agent_id)

        return [
            FeatureValue(
                definition=DEF_INTENT_RISK_SCORE,
                value=float(i_res.intent_risk_score),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_INTENT_CAN_PROCEED,
                value=i_res.can_proceed,
                tenant_id=t_str,
                agent_id=a_str,
            ),
        ]
