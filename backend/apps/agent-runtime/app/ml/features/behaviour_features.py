"""Behaviour Feature Pipeline (Phase 223)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.behaviour_risk_service import BehaviourRiskService
from app.ml.features.base import FeatureCategory, FeatureDefinition, FeatureType, FeatureValue
from app.schemas.behaviour_risk import BehaviourRiskRequest

logger = logging.getLogger("fraudguard.ml.features.behaviour")

DEF_BEHAVIOUR_RISK_SCORE = FeatureDefinition(
    name="behaviour_risk_score",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_BEHAVIOUR_RISK",
    category=FeatureCategory.BEHAVIOUR,
    transformation_description="Authoritative AGENTGUARD behaviour risk score (0.00 to 1.00)",
    version="1.0.0",
)

DEF_BEHAVIOUR_CONFIDENCE = FeatureDefinition(
    name="behaviour_confidence",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_BEHAVIOUR_RISK",
    category=FeatureCategory.BEHAVIOUR,
    transformation_description="Authoritative AGENTGUARD behaviour confidence (0.00 to 1.00)",
    version="1.0.0",
)

DEF_IS_BEHAVIOUR_COLD_START = FeatureDefinition(
    name="is_behaviour_cold_start",
    feature_type=FeatureType.BOOLEAN,
    source="AGENTGUARD_BEHAVIOUR_RISK",
    category=FeatureCategory.BEHAVIOUR,
    transformation_description="True if agent has cold-start behaviour baseline",
    version="1.0.0",
)


class BehaviourFeatureExtractor:
    """Production Behaviour Feature Extractor consuming AGENTGUARD signals (Phase 223)."""

    def __init__(self, behaviour_service: BehaviourRiskService | None = None) -> None:
        self.behaviour_service = behaviour_service or BehaviourRiskService()

    async def extract_features(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        record: dict[str, Any],
    ) -> list[FeatureValue]:
        """Extract ML features consuming AGENTGUARD behaviour engine (Phase 223)."""
        b_req = BehaviourRiskRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            amount=record.get("amount"),
            currency=record.get("currency", "USD"),
            merchant_id=record.get("merchant_id"),
            category=record.get("category"),
        )
        b_res = await self.behaviour_service.calculate_behaviour_risk(db, b_req)

        t_str = str(tenant_id)
        a_str = str(agent_id)

        is_cold_start = b_res.severity == "COLD_START"

        return [
            FeatureValue(
                definition=DEF_BEHAVIOUR_RISK_SCORE,
                value=float(b_res.behaviour_risk_score),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_BEHAVIOUR_CONFIDENCE,
                value=float(b_res.confidence),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_IS_BEHAVIOUR_COLD_START,
                value=is_cold_start,
                tenant_id=t_str,
                agent_id=a_str,
            ),
        ]
