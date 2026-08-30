"""Transaction Risk Score Service (Phase 250)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid

from app.schemas.ml_risk import (
    FraudProbabilityResult,
    TransactionRiskResult,
    TransactionRiskScoreConfig,
)

logger = logging.getLogger("fraudguard.ml.risk.transaction")


class TransactionRiskService:
    """Governed Transaction Risk Scoring Service (Phase 250)."""

    def __init__(self, config: TransactionRiskScoreConfig | None = None) -> None:
        self.config = config or TransactionRiskScoreConfig()

    def _compute_risk_level(self, score: float) -> str:
        """Classify score into deterministic risk band."""
        if score < self.config.low_threshold:
            return "LOW"
        elif score < self.config.medium_threshold:
            return "MEDIUM"
        elif score < self.config.high_threshold:
            return "HIGH"
        else:
            return "CRITICAL"

    def calculate_transaction_risk(
        self,
        probability_result: FraudProbabilityResult,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
        expected_transaction_id: str | None = None,
    ) -> TransactionRiskResult:
        """Calculate governed transaction risk score [0.0, 100.0] from probability [0.0, 1.0] (Phase 250)."""  # noqa: E501
        logger.info(
            "Calculating transaction risk score for tx %s (tenant=%s)",
            probability_result.transaction_id,
            probability_result.tenant_id,
        )

        # 1. Validation of Identity Mismatches
        if expected_tenant_id and probability_result.tenant_id != expected_tenant_id:
            raise ValueError(
                f"Tenant mismatch! Expected {expected_tenant_id}, got {probability_result.tenant_id}"  # noqa: E501
            )

        if expected_agent_id and probability_result.agent_id != expected_agent_id:
            raise ValueError(
                f"Agent mismatch! Expected {expected_agent_id}, got {probability_result.agent_id}"  # noqa: E501
            )

        if expected_transaction_id and probability_result.transaction_id != expected_transaction_id:  # noqa: E501
            raise ValueError(
                f"Transaction ID mismatch! Expected '{expected_transaction_id}', got '{probability_result.transaction_id}'"  # noqa: E501
            )

        # 2. Strict Probability Unit Distinction
        prob = probability_result.fraud_probability
        if math.isnan(prob) or math.isinf(prob) or prob < 0.0 or prob > 1.0:
            raise ValueError(
                f"Unit error: fraud_probability must be in range [0.0, 1.0], got {prob}"
            )  # noqa: E501

        # 3. Deterministic Mapping to Risk Score [0.0, 100.0]
        score = prob * (self.config.score_max - self.config.score_min) + self.config.score_min
        score = round(min(max(score, self.config.score_min), self.config.score_max), 4)

        risk_level = self._compute_risk_level(score)
        sig_id = uuid.uuid4()

        # Config hash computation
        cfg_payload = {
            "score_version": self.config.score_version,
            "min_prob": self.config.minimum_probability,
            "max_prob": self.config.maximum_probability,
            "score_min": self.config.score_min,
            "score_max": self.config.score_max,
            "method": self.config.transformation_method,
            "config_ver": self.config.configuration_version,
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "transaction_risk_score": score,
            "risk_level": risk_level,
            "source_inference_id": str(probability_result.inference_id),
            "tenant_id": str(probability_result.tenant_id),
            "transaction_id": probability_result.transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return TransactionRiskResult(
            risk_signal_id=sig_id,
            tenant_id=probability_result.tenant_id,
            agent_id=probability_result.agent_id,
            transaction_id=probability_result.transaction_id,
            fraud_probability=prob,
            transaction_risk_score=score,
            risk_level=risk_level,
            score_version=self.config.score_version,
            threshold_version=self.config.configuration_version,
            source_inference_id=probability_result.inference_id,
            configuration_hash=cfg_hash,
            result_fingerprint=res_hash,
        )
