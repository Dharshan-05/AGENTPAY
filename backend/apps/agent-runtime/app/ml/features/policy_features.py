"""Policy Risk Features Pipeline (Phase 227)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.policy_evaluation_service import PolicyEvaluationService
from app.ml.features.base import FeatureDefinition, FeatureType, FeatureValue
from app.schemas.policy_evaluation import PolicyEvaluationContext

logger = logging.getLogger("fraudguard.ml.features.policy")

DEF_POLICY_DECISION_CODE = FeatureDefinition(
    name="policy_decision_code",
    feature_type=FeatureType.CATEGORICAL,
    source="POLICY_EVALUATION_SERVICE",
    transformation_description="Policy decision code (ALLOW, DENIED, REQUIRE_APPROVAL, NO_APPLICABLE_POLICY)",  # noqa: E501
    version="1.0.0",
)

DEF_POLICY_REASON_COUNT = FeatureDefinition(
    name="policy_reason_count",
    feature_type=FeatureType.NUMERIC,
    source="POLICY_EVALUATION_SERVICE",
    transformation_description="Count of policy evaluation reason codes",
    version="1.0.0",
)


class PolicyRiskFeatureExtractor:
    """Production Policy Risk Feature Extractor (Phase 227)."""

    def __init__(self, policy_evaluation_service: PolicyEvaluationService | None = None) -> None:
        self.policy_evaluation_service = policy_evaluation_service or PolicyEvaluationService()

    async def extract_features(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        record: dict[str, Any],
    ) -> list[FeatureValue]:
        """Extract policy risk ML features consuming AGENTGUARD policy engine (Phase 227)."""
        ctx = PolicyEvaluationContext(
            tenant_id=tenant_id,
            agent_id=agent_id,
            amount=record.get("amount"),
            currency=record.get("currency", "USD"),
            merchant_id=record.get("merchant_id"),
            category=record.get("category"),
            requested_action=record.get("requested_action", "payment"),
        )
        p_res = await self.policy_evaluation_service.evaluate_policies(db, tenant_id, agent_id, ctx)

        t_str = str(tenant_id)
        a_str = str(agent_id)

        return [
            FeatureValue(
                definition=DEF_POLICY_DECISION_CODE,
                value=p_res.decision,
                tenant_id=t_str,
                agent_id=a_str,
            ),
            FeatureValue(
                definition=DEF_POLICY_REASON_COUNT,
                value=float(len(p_res.reason_codes)),
                tenant_id=t_str,
                agent_id=a_str,
            ),
        ]
