"""Unit & Mandatory Security Tests for Explanation Response Contracts (Phase 262)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.ml.xai.risk_factor_extraction import RiskFactorExtractionService
from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.ml_xai import LocalTransactionExplanation, ShapFeatureImportance


def test_01_explanation_contract_policy_factor_separation() -> None:
    """1. Mandatory Security Test: Policy DENY generates a distinct POLICY factor, maintaining separation from SHAP features."""  # noqa: E501
    service = RiskFactorExtractionService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    shap_imp = ShapFeatureImportance(
        feature_name="amount",
        feature_version="1.0.0",
        shap_value=0.45,
        absolute_importance=0.45,
        relative_importance=1.0,
        direction="POSITIVE",
        rank=1,
    )

    local_exp = LocalTransactionExplanation(
        explanation_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        model_name="mod",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        fraud_probability=0.75,
        transaction_risk_score=75.0,
        risk_level="HIGH",
        top_positive_factors=[shap_imp],
        top_negative_factors=[],
        all_feature_importance=[shap_imp],
        shap_base_value=0.20,
        output_space="MARGIN",
        explanation_statement="Statement",
        prediction_timestamp=now,
        explanation_timestamp=now,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    policy_deny = PolicyRiskResult(
        risk_signal_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_001",
        policy_risk_score=100.0,
        policy_decision="DENY",
        policy_decision_code="SPENDING_LIMIT_EXCEEDED",
        policy_reason_count=1,
        authoritative=True,
        ml_advisory=True,
        allow_ml_scoring=False,
        signal_timestamp=now,
        prediction_timestamp=now,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    res = service.extract_risk_factors(
        tenant_id=t_id,
        transaction_id="tx_001",
        local_explanation=local_exp,
        policy_result=policy_deny,
        agent_id=a_id,
    )

    assert res.has_policy_deny is True
    # Verify Policy factor is separate from MODEL_FEATURE factor
    types = [f.factor_type for f in res.factors]
    assert "POLICY" in types
    assert "MODEL_FEATURE" in types

    pol_f = next(f for f in res.factors if f.factor_type == "POLICY")
    assert pol_f.severity == "CRITICAL"
    assert pol_f.value == 100.0
