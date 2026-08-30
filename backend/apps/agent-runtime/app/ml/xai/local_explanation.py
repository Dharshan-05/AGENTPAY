"""Local Transaction Explanation Service (Phase 258)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime

from app.ml.xai.feature_importance import ShapFeatureImportanceService
from app.schemas.ml_inference import InferenceResult
from app.schemas.ml_risk import TransactionRiskResult
from app.schemas.ml_xai import LocalTransactionExplanation, ShapAttributionResult

logger = logging.getLogger("fraudguard.ml.xai.local")


class LocalTransactionExplanationService:
    """Production Local Transaction Explanation Service (Phase 258)."""

    def __init__(self, importance_service: ShapFeatureImportanceService | None = None) -> None:
        self.importance_service = importance_service or ShapFeatureImportanceService()

    def generate_explanation(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        transaction_id: str,
        prediction_timestamp: datetime,
        inference_result: InferenceResult,
        transaction_risk_result: TransactionRiskResult,
        attribution_result: ShapAttributionResult,
        top_k: int = 5,
    ) -> LocalTransactionExplanation:
        """Generate governed, structured local transaction explanation (Phase 258)."""
        logger.info(
            "Generating local transaction explanation for tx %s (tenant=%s)",
            transaction_id,
            tenant_id,
        )

        # 1. Identity & Isolation Validation
        if inference_result.tenant_id != tenant_id or attribution_result.tenant_id != tenant_id:
            raise ValueError(f"Tenant mismatch! Expected {tenant_id}")

        if transaction_risk_result.transaction_id != transaction_id:
            raise ValueError(f"Transaction ID mismatch! Expected '{transaction_id}'")

        # 2. Point-in-Time Temporal Safety
        p_time = (
            prediction_timestamp.replace(tzinfo=UTC)
            if prediction_timestamp.tzinfo is None
            else prediction_timestamp
        )  # noqa: E501
        inf_time = (
            inference_result.prediction_timestamp.replace(tzinfo=UTC)
            if inference_result.prediction_timestamp.tzinfo is None
            else inference_result.prediction_timestamp
        )  # noqa: E501

        if inf_time > p_time:
            raise ValueError("Point-in-time violation: inference timestamp is in the future!")

        # 3. Rank Feature Importances
        all_importance = self.importance_service.compute_feature_importance(attribution_result)

        pos_factors = [item for item in all_importance if item.direction == "POSITIVE"][:top_k]
        neg_factors = [item for item in all_importance if item.direction == "NEGATIVE"][:top_k]

        # 4. Construct Non-Causal Explanation Statement
        pos_names = [f.feature_name for f in pos_factors]
        neg_names = [f.feature_name for f in neg_factors]

        stmt = (
            f"Features {pos_names} contributed positively to the model's fraud-risk prediction "
            f"(risk level: {transaction_risk_result.risk_level}, P(fraud): {inference_result.fraud_probability:.4f}). "  # noqa: E501
            f"Features {neg_names} mitigated predicted risk."
        )

        exp_id = uuid.uuid4()
        now = datetime.now(UTC)

        cfg_payload = {"top_k": top_k, "version": "1.0.0"}
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "transaction_id": transaction_id,
            "tenant_id": str(tenant_id),
            "fraud_probability": inference_result.fraud_probability,
            "risk_level": transaction_risk_result.risk_level,
            "top_positive": pos_names,
            "top_negative": neg_names,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return LocalTransactionExplanation(
            explanation_id=exp_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            model_name=inference_result.model_id,
            model_version=inference_result.model_version,
            artifact_checksum=attribution_result.artifact_checksum,
            fraud_probability=inference_result.fraud_probability,
            transaction_risk_score=transaction_risk_result.transaction_risk_score,
            risk_level=transaction_risk_result.risk_level,
            top_positive_factors=pos_factors,
            top_negative_factors=neg_factors,
            all_feature_importance=all_importance,
            shap_base_value=attribution_result.base_value,
            output_space=attribution_result.output_space,
            explanation_statement=stmt,
            prediction_timestamp=p_time,
            explanation_timestamp=now,
            configuration_hash=cfg_hash,
            result_fingerprint=res_hash,
        )
