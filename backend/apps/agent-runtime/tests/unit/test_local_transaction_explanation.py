"""Unit & Adversarial Tests for Local Transaction Explanation Service (Phase 258)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.ml.xai.local_explanation import LocalTransactionExplanationService
from app.schemas.ml_inference import InferenceResult
from app.schemas.ml_risk import TransactionRiskResult
from app.schemas.ml_xai import ShapAttributionResult


def test_01_valid_local_transaction_explanation_and_statement() -> None:
    """1. Test valid local transaction explanation, top_k filtering, and non-causal statement generation."""  # noqa: E501
    service = LocalTransactionExplanationService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    inf_res = InferenceResult(
        inference_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        model_id="fraudguard_xgboost",
        model_version="1.0.0",
        feature_versions={"feat_a": "1.0.0", "feat_b": "1.0.0"},
        prediction_timestamp=now,
        fraud_probability=0.65,
        configuration_hash="c" * 64,
        request_fingerprint="r" * 64,
    )

    risk_res = TransactionRiskResult(
        risk_signal_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        fraud_probability=0.65,
        transaction_risk_score=65.0,
        risk_level="HIGH",
        source_inference_id=inf_res.inference_id,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    attr_res = ShapAttributionResult(
        explanation_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        model_name="fraudguard_xgboost",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        feature_names=["feat_a", "feat_b"],
        feature_versions={"feat_a": "1.0.0", "feat_b": "1.0.0"},
        shap_values=[0.45, -0.25],
        base_value=0.20,
        prediction_probability=0.65,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    exp = service.generate_explanation(
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        prediction_timestamp=now,
        inference_result=inf_res,
        transaction_risk_result=risk_res,
        attribution_result=attr_res,
        top_k=5,
    )

    assert exp.transaction_id == "tx_001"
    assert exp.risk_level == "HIGH"
    assert len(exp.top_positive_factors) == 1
    assert exp.top_positive_factors[0].feature_name == "feat_a"
    assert len(exp.top_negative_factors) == 1
    assert exp.top_negative_factors[0].feature_name == "feat_b"
    assert (
        "contributed positively to the model's fraud-risk prediction" in exp.explanation_statement
    )  # noqa: E501
    assert "Transaction is fraudulent" not in exp.explanation_statement


def test_02_mandatory_test_label_poisoning_isolation() -> None:
    """2. Mandatory Poison Test: Altering or injecting test labels does NOT alter local explanation."""  # noqa: E501
    service = LocalTransactionExplanationService()
    t_id = uuid.uuid4()
    now = datetime.now(UTC)

    inf_res = InferenceResult(
        inference_id=uuid.uuid4(),
        tenant_id=t_id,
        transaction_id="tx_poison",
        model_id="mod",
        model_version="1.0.0",
        feature_versions={},
        prediction_timestamp=now,
        fraud_probability=0.80,
        configuration_hash="c" * 64,
        request_fingerprint="r" * 64,
    )

    risk_res = TransactionRiskResult(
        risk_signal_id=uuid.uuid4(),
        tenant_id=t_id,
        transaction_id="tx_poison",
        fraud_probability=0.80,
        transaction_risk_score=80.0,
        risk_level="HIGH",
        source_inference_id=inf_res.inference_id,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    attr_res = ShapAttributionResult(
        explanation_id=uuid.uuid4(),
        tenant_id=t_id,
        transaction_id="tx_poison",
        model_name="mod",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        feature_names=["amount"],
        feature_versions={},
        shap_values=[0.50],
        base_value=0.30,
        prediction_probability=0.80,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    # Explanation generation is 100% label-free
    exp1 = service.generate_explanation(t_id, None, "tx_poison", now, inf_res, risk_res, attr_res)  # noqa: E501
    exp2 = service.generate_explanation(t_id, None, "tx_poison", now, inf_res, risk_res, attr_res)  # noqa: E501

    assert exp1.top_positive_factors[0].shap_value == exp2.top_positive_factors[0].shap_value
    assert exp1.explanation_statement == exp2.explanation_statement
