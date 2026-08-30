"""Agent Trust & Risk Profile Features Pipeline (Phase 228)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

from app.application.services.agent_risk_profile_service import AgentRiskProfileService
from app.application.services.agent_trust_score_service import AgentTrustScoreService
from app.ml.features.base import FeatureDefinition, FeatureType, FeatureValue

logger = logging.getLogger("fraudguard.ml.features.trust")

DEF_TRUST_SCORE = FeatureDefinition(
    name="trust_score",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_TRUST_SCORE",
    transformation_description="Authoritative AGENTGUARD trust score (0.00 to 1.00)",
    version="1.0.0",
)

DEF_RISK_SCORE = FeatureDefinition(
    name="risk_score",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_RISK_PROFILE",
    transformation_description="Authoritative AGENTGUARD risk score distinct from trust score",
    version="1.0.0",
)

DEF_RISK_LEVEL = FeatureDefinition(
    name="risk_level",
    feature_type=FeatureType.CATEGORICAL,
    source="AGENTGUARD_RISK_PROFILE",
    transformation_description="Risk level state classification (LOW, NORMAL, ELEVATED, HIGH, CRITICAL, COLD_START)",  # noqa: E501
    version="1.0.0",
)


class AgentTrustFeatureExtractor:
    """Production Agent Trust Feature Extractor (Phase 228)."""

    def __init__(
        self,
        trust_service: AgentTrustScoreService | None = None,
        profile_service: AgentRiskProfileService | None = None,
    ) -> None:
        self.trust_service = trust_service or AgentTrustScoreService()
        self.profile_service = profile_service or AgentRiskProfileService()

    def extract_features(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        trust_score_val: Decimal = Decimal("1.00"),
    ) -> list[FeatureValue]:
        """Extract trust and risk features consuming AGENTGUARD trust & profile services (Phase 228)."""  # noqa: E501
        profile = self.profile_service.build_risk_profile(
            tenant_id=tenant_id,
            agent_id=agent_id,
            trust_score=trust_score_val,
        )

        t_str = str(tenant_id)
        a_str = str(agent_id)

        return [
            FeatureValue(
                definition=DEF_TRUST_SCORE,
                value=float(trust_score_val),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_RISK_SCORE,
                value=float(profile.risk_score),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_RISK_LEVEL,
                value=profile.risk_level,
                tenant_id=t_str,
                agent_id=a_str,
            ),
        ]
