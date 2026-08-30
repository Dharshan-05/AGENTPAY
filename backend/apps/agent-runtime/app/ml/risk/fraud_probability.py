"""Fraud Probability Domain Service (Phase 249)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid

from app.schemas.ml_inference import InferenceResult
from app.schemas.ml_risk import FraudProbabilityResult

logger = logging.getLogger("fraudguard.ml.risk.probability")


class FraudProbabilityService:
    """Production Fraud Probability Service validating Inference outcomes (Phase 249)."""

    def process_inference_probability(
        self,
        inference_result: InferenceResult,
        expected_tenant_id: uuid.UUID | None = None,
        expected_agent_id: uuid.UUID | None = None,
        expected_transaction_id: str | None = None,
    ) -> FraudProbabilityResult:
        """Validate and extract raw model fraud probability from InferenceResult (Phase 249)."""
        logger.info(
            "Processing fraud probability for inference %s (tx=%s)",
            inference_result.inference_id,
            inference_result.transaction_id,
        )

        # 1. Validation of Context Identity Matching
        if expected_tenant_id and inference_result.tenant_id != expected_tenant_id:
            logger.error(
                "Tenant mismatch: inference tenant %s != expected %s",
                inference_result.tenant_id,
                expected_tenant_id,
            )  # noqa: E501
            raise ValueError(
                f"Tenant mismatch! Inference belongs to tenant {inference_result.tenant_id}"
            )  # noqa: E501

        if expected_agent_id and inference_result.agent_id != expected_agent_id:
            logger.error(
                "Agent mismatch: inference agent %s != expected %s",
                inference_result.agent_id,
                expected_agent_id,
            )  # noqa: E501
            raise ValueError(
                f"Agent mismatch! Inference belongs to agent {inference_result.agent_id}"
            )  # noqa: E501

        if expected_transaction_id and inference_result.transaction_id != expected_transaction_id:
            raise ValueError(
                f"Transaction ID mismatch! Expected '{expected_transaction_id}', got '{inference_result.transaction_id}'"  # noqa: E501
            )

        # 2. Probability Range & Safety Validation
        prob = inference_result.fraud_probability
        if math.isnan(prob) or math.isinf(prob):
            raise ValueError(f"Invalid probability value: {prob}")

        if prob < 0.0 or prob > 1.0:
            raise ValueError(f"Probability out of bounds [0.0, 1.0]: {prob}")

        sig_id = uuid.uuid4()
        prob = round(prob, 6)

        # 3. Canonical Fingerprints
        src_payload = {
            "inference_id": str(inference_result.inference_id),
            "tenant_id": str(inference_result.tenant_id),
            "transaction_id": inference_result.transaction_id,
            "request_fingerprint": inference_result.request_fingerprint,
        }
        src_hash = hashlib.sha256(json.dumps(src_payload, sort_keys=True).encode()).hexdigest()

        cfg_hash = inference_result.configuration_hash

        res_payload = {
            "fraud_probability": prob,
            "model_version": inference_result.model_version,
            "tenant_id": str(inference_result.tenant_id),
            "source_fingerprint": src_hash,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return FraudProbabilityResult(
            risk_signal_id=sig_id,
            inference_id=inference_result.inference_id,
            tenant_id=inference_result.tenant_id,
            agent_id=inference_result.agent_id,
            transaction_id=inference_result.transaction_id,
            model_id=inference_result.model_id,
            model_version=inference_result.model_version,
            fraud_probability=prob,
            probability_version="1.0.0",
            configuration_hash=cfg_hash,
            source_fingerprint=src_hash,
            result_fingerprint=res_hash,
        )
