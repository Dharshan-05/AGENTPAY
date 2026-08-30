"""Velocity Risk Features Pipeline (Phase 225)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.velocity_risk_service import VelocityRiskService
from app.ml.features.base import FeatureDefinition, FeatureType, FeatureValue
from app.schemas.velocity_risk import VelocityRiskRequest

logger = logging.getLogger("fraudguard.ml.features.velocity")

DEF_VELOCITY_RISK_SCORE = FeatureDefinition(
    name="velocity_risk_score",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_VELOCITY_RISK",
    transformation_description="Authoritative AGENTGUARD velocity risk score (0.00 to 1.00)",
    version="1.0.0",
)

DEF_IS_BURST_DETECTED = FeatureDefinition(
    name="is_burst_detected",
    feature_type=FeatureType.BOOLEAN,
    source="AGENTGUARD_VELOCITY_RISK",
    transformation_description="True if short-window transaction burst detected",
    version="1.0.0",
)


class VelocityFeatureExtractor:
    """Production Velocity Feature Extractor (Phase 225)."""

    def __init__(self, velocity_risk_service: VelocityRiskService | None = None) -> None:
        self.velocity_risk_service = velocity_risk_service or VelocityRiskService()

    async def extract_features(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        window_minutes: int = 60,
    ) -> list[FeatureValue]:
        """Extract velocity features consuming AGENTGUARD velocity risk engine (Phase 225)."""
        v_req = VelocityRiskRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            window_minutes=window_minutes,
        )
        v_res = await self.velocity_risk_service.calculate_velocity_risk(db, v_req)

        t_str = str(tenant_id)
        a_str = str(agent_id)

        return [
            FeatureValue(
                definition=DEF_VELOCITY_RISK_SCORE,
                value=float(v_res.velocity_risk_score),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_IS_BURST_DETECTED,
                value=v_res.burst_detected,
                tenant_id=t_str,
                agent_id=a_str,
            ),
        ]
