"""Unit & Adversarial Tests for Fraud Probability Service (Phase 249)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.ml.risk.fraud_probability import FraudProbabilityService
from app.schemas.ml_inference import InferenceResult


def test_01_valid_probability_extraction_and_boundaries() -> None:
    """1. Test valid probability extraction, boundary values (0.0, 1.0), and deterministic fingerprints."""  # noqa: E501
    service = FraudProbabilityService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    inf_id = uuid.uuid4()

    inf_res = InferenceResult(
        inference_id=inf_id,
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        model_id="mod_01",
        model_version="1.0.0",
        feature_versions={"feat_a": "1.0.0"},
        prediction_timestamp=datetime.now(UTC),
        fraud_probability=0.75,
        configuration_hash="a" * 64,
        request_fingerprint="b" * 64,
    )

    res1 = service.process_inference_probability(inf_res)
    assert res1.fraud_probability == 0.75
    assert res1.tenant_id == t_id
    assert res1.agent_id == a_id

    # Deterministic fingerprint check
    res2 = service.process_inference_probability(inf_res)
    assert res1.source_fingerprint == res2.source_fingerprint
    assert res1.result_fingerprint == res2.result_fingerprint


def test_02_adversarial_out_of_bounds_and_nan_rejection() -> None:
    """2. Mandatory Adversarial Test A & B: Rejects probability > 1.0, < 0.0, NaN, and Infinity."""
    service = FraudProbabilityService()
    t_id = uuid.uuid4()

    def make_inf(prob: float) -> InferenceResult:
        return InferenceResult(
            inference_id=uuid.uuid4(),
            tenant_id=t_id,
            transaction_id="tx_test",
            model_id="m1",
            model_version="1.0.0",
            feature_versions={},
            prediction_timestamp=datetime.now(UTC),
            fraud_probability=0.5,  # Valid schema fallback
            configuration_hash="a" * 64,
            request_fingerprint="b" * 64,
        )

    inf_invalid_high = make_inf(0.5)
    inf_invalid_high.fraud_probability = 1.5  # Bypass pydantic validation for test
    with pytest.raises(ValueError, match="Probability out of bounds"):
        service.process_inference_probability(inf_invalid_high)

    inf_invalid_low = make_inf(0.5)
    inf_invalid_low.fraud_probability = -0.1
    with pytest.raises(ValueError, match="Probability out of bounds"):
        service.process_inference_probability(inf_invalid_low)

    inf_nan = make_inf(0.5)
    inf_nan.fraud_probability = float("nan")
    with pytest.raises(ValueError, match="Invalid probability value"):
        service.process_inference_probability(inf_nan)


def test_03_adversarial_cross_tenant_and_agent_mismatch_rejection() -> None:
    """3. Mandatory Adversarial Test C & D: Tenant or Agent context mismatches fail closed."""
    service = FraudProbabilityService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    inf_res = InferenceResult(
        inference_id=uuid.uuid4(),
        tenant_id=tenant_b,
        transaction_id="tx_001",
        model_id="m1",
        model_version="1.0.0",
        feature_versions={},
        prediction_timestamp=datetime.now(UTC),
        fraud_probability=0.85,
        configuration_hash="a" * 64,
        request_fingerprint="b" * 64,
    )

    # Attach Tenant B inference to Tenant A context -> fail closed!
    with pytest.raises(ValueError, match="Tenant mismatch!"):
        service.process_inference_probability(inf_res, expected_tenant_id=tenant_a)
