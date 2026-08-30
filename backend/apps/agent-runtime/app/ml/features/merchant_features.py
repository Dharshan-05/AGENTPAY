"""Merchant Risk Features Pipeline (Phase 224)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.merchant_behaviour_analysis_service import (
    MerchantBehaviourAnalysisService,
)
from app.ml.features.base import FeatureDefinition, FeatureType, FeatureValue
from app.schemas.merchant_behaviour_analysis import (
    MerchantBehaviourAnalysisRequest,
)

logger = logging.getLogger("fraudguard.ml.features.merchant")

DEF_MERCHANT_FAMILIARITY_SCORE = FeatureDefinition(
    name="merchant_familiarity_score",
    feature_type=FeatureType.NUMERIC,
    source="AGENTGUARD_MERCHANT_ANALYSIS",
    transformation_description="Merchant familiarity score from AGENTGUARD analysis (0.00 to 1.00)",
    version="1.0.0",
)

DEF_IS_NEW_MERCHANT = FeatureDefinition(
    name="is_new_merchant",
    feature_type=FeatureType.BOOLEAN,
    source="AGENTGUARD_MERCHANT_ANALYSIS",
    transformation_description="True if agent has no prior transaction history with merchant",
    version="1.0.0",
)


class MerchantRiskFeatureExtractor:
    """Production Merchant Risk Feature Extractor (Phase 224)."""

    def __init__(self, merchant_service: MerchantBehaviourAnalysisService | None = None) -> None:
        self.merchant_service = merchant_service or MerchantBehaviourAnalysisService()

    async def extract_features(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        merchant_id: uuid.UUID | None,
    ) -> list[FeatureValue]:
        """Extract merchant risk features consuming AGENTGUARD merchant analysis (Phase 224)."""
        t_str = str(tenant_id)
        a_str = str(agent_id)

        if not merchant_id:
            return [
                FeatureValue(
                    definition=DEF_MERCHANT_FAMILIARITY_SCORE,
                    value=0.50,
                    tenant_id=t_str,
                    agent_id=a_str,
                ),
                FeatureValue(
                    definition=DEF_IS_NEW_MERCHANT,
                    value=True,
                    tenant_id=t_str,
                    agent_id=a_str,
                ),
            ]

        m_req = MerchantBehaviourAnalysisRequest(
            tenant_id=tenant_id,
            agent_id=agent_id,
            merchant_id=merchant_id,
        )
        m_res = await self.merchant_service.analyze_merchant_behaviour(db, m_req)

        is_new = m_res.familiarity in ("FIRST_SEEN", "UNFAMILIAR", "INSUFFICIENT_DATA")

        return [
            FeatureValue(
                definition=DEF_MERCHANT_FAMILIARITY_SCORE,
                value=float(m_res.merchant_score),
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_IS_NEW_MERCHANT,
                value=is_new,
                tenant_id=t_str,
                agent_id=a_str,
            ),
        ]
