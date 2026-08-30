"""Unit & Mandatory Security Precedence Tests for Risk Factor Extraction (Phase 260)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.ml.xai.risk_factor_extraction import RiskFactorExtractionService
from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.ml_xai import LocalTransactionExplanation, ShapFeatureImportance


def test_01_risk_factor_extraction_and_policy_deny_precedence() -> None:
    """1. Mandatory Security Test: Policy DENY generates CRITICAL Policy Risk Factor & preserves DENY precedence."""  # noqa: E501
    service = RiskFactorExtractionService()
    t_id = uuid.uuid4()
    a_id = uuid.uuid4()
    now = datetime.now(UTC)

    shap_imp = ShapFeatureImportance(
        feature_name="amount",
        feature_version="1.0.0",
        shap_value=0.55,
        absolute_importance=0.55,
        relative_importance=1.0,
        direction="POSITIVE",
        rank=1,
    )

    local_exp = LocalTransactionExplanation(
        explanation_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_deny_001",
        model_name="mod",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        fraud_probability=0.85,
        transaction_risk_score=85.0,
        risk_level="HIGH",
        top_positive_factors=[shap_imp],
        top_negative_factors=[],
        all_feature_importance=[shap_imp],
        shap_base_value=0.30,
        output_space="MARGIN",
        explanation_statement="Risk high",
        prediction_timestamp=now,
        explanation_timestamp=now,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    policy_deny = PolicyRiskResult(
        risk_signal_id=uuid.uuid4(),
        tenant_id=t_id,
        agent_id=a_id,
        transaction_id="tx_deny_001",
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
        transaction_id="tx_deny_001",
        local_explanation=local_exp,
        policy_result=policy_deny,
        agent_id=a_id,
    )

    assert res.has_policy_deny is True
    assert len(res.factors) == 2
    # Verify policy factor exists with CRITICAL severity
    policy_factor = next(f for f in res.factors if f.factor_type == "POLICY")
    assert policy_factor.severity == "CRITICAL"
    assert policy_factor.feature_name == "policy_decision"
    assert policy_factor.source == "AGENTGUARD_POLICY_ENGINE"

    # Verify SHAP model feature factor exists separately
    model_factor = next(f for f in res.factors if f.factor_type == "MODEL_FEATURE")
    assert model_factor.feature_name == "amount"
    assert model_factor.shap_value == 0.55


def test_02_tenant_mismatch_rejection() -> None:
    """2. Mandatory Test: Rejects tenant mismatches during risk factor extraction."""
    service = RiskFactorExtractionService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    now = datetime.now(UTC)

    local_exp = LocalTransactionExplanation(
        explanation_id=uuid.uuid4(),
        tenant_id=tenant_a,
        transaction_id="tx_001",
        model_name="mod",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        fraud_probability=0.50,
        transaction_risk_score=50.0,
        risk_level="MEDIUM",
        top_positive_factors=[],
        top_negative_factors=[],
        all_feature_importance=[],
        shap_base_value=0.10,
        output_space="MARGIN",
        explanation_statement="Statement",
        prediction_timestamp=now,
        explanation_timestamp=now,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Tenant mismatch!"):
        service.extract_risk_factors(
            tenant_id=tenant_b,  # Mismatched tenant!
            transaction_id="tx_001",
            local_explanation=local_exp,
        )
