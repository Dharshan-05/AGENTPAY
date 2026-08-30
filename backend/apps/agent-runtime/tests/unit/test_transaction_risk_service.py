"""Unit & Adversarial Tests for Transaction Risk Score Service (Phase 250)."""

from __future__ import annotations

import uuid

import pytest

from app.ml.risk.transaction_risk import TransactionRiskService
from app.schemas.ml_risk import FraudProbabilityResult


def test_01_valid_transaction_risk_score_and_risk_bands() -> None:
    """1. Test valid transaction risk score calculation [0.0, 100.0] and risk band classification."""  # noqa: E501
    service = TransactionRiskService()
    t_id = uuid.uuid4()

    def make_prob_res(prob: float) -> FraudProbabilityResult:
        return FraudProbabilityResult(
            risk_signal_id=uuid.uuid4(),
            inference_id=uuid.uuid4(),
            tenant_id=t_id,
            transaction_id="tx_001",
            model_id="m1",
            model_version="1.0.0",
            fraud_probability=prob,
            configuration_hash="a" * 64,
            source_fingerprint="b" * 64,
            result_fingerprint="c" * 64,
        )

    # LOW risk (0.10 -> score 10.0)
    res_low = service.calculate_transaction_risk(make_prob_res(0.10))
    assert res_low.transaction_risk_score == 10.0
    assert res_low.risk_level == "LOW"

    # MEDIUM risk (0.35 -> score 35.0)
    res_med = service.calculate_transaction_risk(make_prob_res(0.35))
    assert res_med.transaction_risk_score == 35.0
    assert res_med.risk_level == "MEDIUM"

    # HIGH risk (0.60 -> score 60.0)
    res_high = service.calculate_transaction_risk(make_prob_res(0.60))
    assert res_high.transaction_risk_score == 60.0
    assert res_high.risk_level == "HIGH"

    # CRITICAL risk (0.85 -> score 85.0)
    res_crit = service.calculate_transaction_risk(make_prob_res(0.85))
    assert res_crit.transaction_risk_score == 85.0
    assert res_crit.risk_level == "CRITICAL"


def test_02_unit_distinction_and_mismatch_rejection() -> None:
    """2. Mandatory Test: Probability vs Score unit distinction and transaction ID mismatch rejection."""  # noqa: E501
    service = TransactionRiskService()
    t_id = uuid.uuid4()

    prob_res = FraudProbabilityResult(
        risk_signal_id=uuid.uuid4(),
        inference_id=uuid.uuid4(),
        tenant_id=t_id,
        transaction_id="tx_target_123",
        model_id="m1",
        model_version="1.0.0",
        fraud_probability=0.50,
        configuration_hash="a" * 64,
        source_fingerprint="b" * 64,
        result_fingerprint="c" * 64,
    )

    # Supplying wrong expected_transaction_id fails closed
    with pytest.raises(ValueError, match="Transaction ID mismatch!"):
        service.calculate_transaction_risk(prob_res, expected_transaction_id="tx_other_456")

    # Invalid probability (e.g. 50.0 instead of 0.50) fails unit check
    prob_res_invalid = prob_res.model_copy(update={"fraud_probability": 50.0})
    with pytest.raises(ValueError, match="Unit error: fraud_probability must be in range"):
        service.calculate_transaction_risk(prob_res_invalid)
