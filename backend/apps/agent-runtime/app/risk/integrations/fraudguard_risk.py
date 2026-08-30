"""FraudGuard Risk Integration Adapter (Phase 269)."""

from __future__ import annotations

import logging
import math
import uuid
from typing import Any

from app.schemas.fraudguard_api import (
    FraudGuardInferenceResponse,
    FraudGuardRiskIntelligenceResponse,
)
from app.schemas.ml_inference import InferenceResult
from app.schemas.ml_risk import FraudProbabilityResult, TransactionRiskResult
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
    RiskSignalType,
)

logger = logging.getLogger("agentpay.risk.integrations.fraudguard")

PROHIBITED_TARGET_FIELDS: frozenset[str] = frozenset(
    {
        "is_fraud",
        "fraud_label",
        "post_outcome",
        "chargeback_result",
        "investigation_result",
        "future_outcome",
    }
)


class FraudGuardRiskIntegrationService:
    """Production FraudGuard Risk Integration Adapter (Phase 269)."""

    def _inspect_target_leakage(self, metadata: dict[str, Any]) -> None:
        """Inspect metadata for prohibited data leakage fields."""
        if not metadata:
            return
        for k, v in metadata.items():
            k_lower = str(k).lower()
            if k_lower in PROHIBITED_TARGET_FIELDS:
                raise ValueError(f"Prohibited target leakage field '{k}' detected in metadata.")
            v_str = str(v).lower()
            for target_field in PROHIBITED_TARGET_FIELDS:
                if target_field in v_str:
                    raise ValueError(
                        f"Prohibited target leakage value '{v_str}' detected in metadata field '{k}'."  # noqa: E501
                    )

    def _validate_numeric(self, val: float | None, name: str) -> float | None:
        """Validate numeric float against NaN and Infinity."""
        if val is None:
            return None
        val_float = float(val)
        if math.isnan(val_float) or math.isinf(val_float):
            raise ValueError(f"NaN or Infinity value detected for '{name}'.")
        return val_float

    def integrate_fraud_probability(
        self,
        result: FraudProbabilityResult,
        context: RiskEvaluationContext,
    ) -> RiskSignal:
        """Convert authoritative FraudProbabilityResult into canonical RiskSignal (Phase 269)."""
        logger.info(
            "Integrating FraudProbabilityResult for tx %s (tenant=%s)",
            result.transaction_id,
            result.tenant_id,
        )

        # 1. Identity Binding Security Check
        if result.tenant_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! FraudGuard tenant '{result.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if result.agent_id and result.agent_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! FraudGuard agent '{result.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )
        if result.transaction_id != context.transaction_id:
            raise ValueError(
                f"Transaction ID mismatch! FraudGuard tx '{result.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
            )

        # 2. Point-in-Time Timestamp Security Check
        if result.generated_at > context.prediction_timestamp:
            raise ValueError(
                f"FraudGuard signal timestamp '{result.generated_at.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        # 3. Probability Safety & Bounds Validation
        prob = self._validate_numeric(result.fraud_probability, "fraud_probability")
        if prob is None or prob < 0.0 or prob > 1.0:
            raise ValueError(f"Fraud probability {prob} out of valid range [0.0, 1.0].")

        metadata = {
            "model_id": result.model_id,
            "model_version": result.model_version,
            "inference_id": str(result.inference_id),
            "configuration_hash": result.configuration_hash,
        }
        self._inspect_target_leakage(metadata)

        return RiskSignal(
            signal_type=RiskSignalType.FRAUDGUARD,
            source="FRAUDGUARD",
            score=prob,
            score_unit=RiskScoreUnit.PROBABILITY,
            normalized_score=prob * 100.0,
            timestamp=result.generated_at,
            tenant_id=result.tenant_id,
            agent_id=context.agent_id,
            transaction_id=result.transaction_id,
            source_version=result.model_version,
            source_fingerprint=result.result_fingerprint,
            metadata=metadata,
        )

    def integrate_transaction_risk_result(
        self,
        result: TransactionRiskResult,
        context: RiskEvaluationContext,
    ) -> RiskSignal:
        """Convert authoritative TransactionRiskResult into canonical RiskSignal (Phase 269)."""
        logger.info(
            "Integrating TransactionRiskResult for tx %s (tenant=%s)",
            result.transaction_id,
            result.tenant_id,
        )

        # 1. Identity Binding Security Check
        if result.tenant_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! Transaction risk tenant '{result.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if result.agent_id and result.agent_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! Transaction risk agent '{result.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )
        if result.transaction_id != context.transaction_id:
            raise ValueError(
                f"Transaction ID mismatch! Transaction risk tx '{result.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
            )

        # 2. Point-in-Time Timestamp Security Check
        if result.generated_at > context.prediction_timestamp:
            raise ValueError(
                f"Transaction risk signal timestamp '{result.generated_at.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        # 3. Transaction Risk Score Bounds Validation
        risk_score = self._validate_numeric(result.transaction_risk_score, "transaction_risk_score")  # noqa: E501
        if risk_score is None or risk_score < 0.0 or risk_score > 100.0:
            raise ValueError(
                f"Transaction risk score {risk_score} out of valid range [0.0, 100.0]."
            )

        metadata = {
            "fraud_probability": result.fraud_probability,
            "risk_level": result.risk_level,
            "score_version": result.score_version,
            "threshold_version": result.threshold_version,
            "source_inference_id": str(result.source_inference_id),
        }
        self._inspect_target_leakage(metadata)

        return RiskSignal(
            signal_type=RiskSignalType.TRANSACTION,
            source="FRAUDGUARD",
            score=risk_score,
            score_unit=RiskScoreUnit.RISK_SCORE,
            normalized_score=risk_score,
            timestamp=result.generated_at,
            tenant_id=result.tenant_id,
            agent_id=context.agent_id,
            transaction_id=result.transaction_id,
            source_version=result.score_version,
            source_fingerprint=result.result_fingerprint,
            metadata=metadata,
        )

    def integrate_inference_result(
        self,
        result: InferenceResult | FraudGuardInferenceResponse,
        context: RiskEvaluationContext,
    ) -> RiskSignal:
        """Convert authoritative InferenceResult or FraudGuardInferenceResponse into canonical RiskSignal (Phase 269)."""  # noqa: E501
        logger.info(
            "Integrating InferenceResult for tx %s (tenant=%s)",
            result.transaction_id,
            result.tenant_id,
        )

        # 1. Identity Binding Security Check
        if result.tenant_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! Inference tenant '{result.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if result.agent_id and result.agent_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! Inference agent '{result.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )
        if result.transaction_id != context.transaction_id:
            raise ValueError(
                f"Transaction ID mismatch! Inference tx '{result.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
            )

        # 2. Point-in-Time Timestamp Security Check
        ts = getattr(result, "prediction_timestamp", getattr(result, "inference_timestamp", None))
        if ts is None:
            ts = context.prediction_timestamp
        if ts > context.prediction_timestamp:
            raise ValueError(
                f"Inference signal timestamp '{ts.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        # 3. Probability Bounds Validation
        prob = self._validate_numeric(result.fraud_probability, "fraud_probability")
        if prob is None or prob < 0.0 or prob > 1.0:
            raise ValueError(f"Inference fraud probability {prob} out of valid range [0.0, 1.0].")

        model_name = getattr(
            result, "model_name", getattr(result, "model_id", "fraudguard_xgboost")
        )  # noqa: E501
        model_version = result.model_version
        inf_id = getattr(result, "inference_id", uuid.uuid4())
        fp = getattr(result, "result_fingerprint", getattr(result, "request_fingerprint", ""))

        metadata = {
            "model_name": model_name,
            "model_version": model_version,
            "inference_id": str(inf_id),
            "artifact_checksum": getattr(result, "artifact_checksum", None),
        }
        self._inspect_target_leakage(metadata)

        return RiskSignal(
            signal_type=RiskSignalType.FRAUDGUARD,
            source="FRAUDGUARD",
            score=prob,
            score_unit=RiskScoreUnit.PROBABILITY,
            normalized_score=prob * 100.0,
            timestamp=ts,
            tenant_id=result.tenant_id,
            agent_id=context.agent_id,
            transaction_id=result.transaction_id,
            source_version=model_version,
            source_fingerprint=fp,
            metadata=metadata,
        )

    def integrate_risk_intelligence_response(
        self,
        response: FraudGuardRiskIntelligenceResponse,
        context: RiskEvaluationContext,
    ) -> list[RiskSignal]:
        """Convert comprehensive FraudGuardRiskIntelligenceResponse into canonical RiskSignal objects (Phase 269)."""  # noqa: E501
        logger.info(
            "Integrating FraudGuardRiskIntelligenceResponse for tx %s (tenant=%s)",
            response.transaction_id,
            response.tenant_id,
        )

        # 1. Identity Binding Security Check
        if response.tenant_id != context.tenant_id:
            raise ValueError(
                f"Tenant ID mismatch! Risk intelligence tenant '{response.tenant_id}' != context tenant '{context.tenant_id}'"  # noqa: E501
            )
        if response.agent_id and response.agent_id != context.agent_id:
            raise ValueError(
                f"Agent ID mismatch! Risk intelligence agent '{response.agent_id}' != context agent '{context.agent_id}'"  # noqa: E501
            )
        if response.transaction_id != context.transaction_id:
            raise ValueError(
                f"Transaction ID mismatch! Risk intelligence tx '{response.transaction_id}' != context tx '{context.transaction_id}'"  # noqa: E501
            )

        # 2. Point-in-Time Timestamp Security Check
        ts = response.evaluated_at
        if ts > context.prediction_timestamp:
            raise ValueError(
                f"Risk intelligence timestamp '{ts.isoformat()}' is in the future relative to prediction timestamp '{context.prediction_timestamp.isoformat()}'"  # noqa: E501
            )

        signals: list[RiskSignal] = []

        # 1. Fraud Probability Signal
        prob = self._validate_numeric(response.fraud_probability, "fraud_probability")
        if prob is not None:
            if prob < 0.0 or prob > 1.0:
                raise ValueError(f"Fraud probability {prob} out of valid range [0.0, 1.0].")
            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.FRAUDGUARD,
                    source="FRAUDGUARD",
                    score=prob,
                    score_unit=RiskScoreUnit.PROBABILITY,
                    normalized_score=prob * 100.0,
                    timestamp=ts,
                    tenant_id=response.tenant_id,
                    agent_id=context.agent_id,
                    transaction_id=response.transaction_id,
                    source_fingerprint=response.result_fingerprint,
                )
            )

        # 2. Transaction Risk Score Signal
        risk = self._validate_numeric(response.transaction_risk_score, "transaction_risk_score")
        if risk is not None:
            if risk < 0.0 or risk > 100.0:
                raise ValueError(f"Transaction risk score {risk} out of valid range [0.0, 100.0].")
            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.TRANSACTION,
                    source="FRAUDGUARD",
                    score=risk,
                    score_unit=RiskScoreUnit.RISK_SCORE,
                    normalized_score=risk,
                    timestamp=ts,
                    tenant_id=response.tenant_id,
                    agent_id=context.agent_id,
                    transaction_id=response.transaction_id,
                    source_fingerprint=response.result_fingerprint,
                    metadata={"risk_level": response.risk_level},
                )
            )

        return signals
