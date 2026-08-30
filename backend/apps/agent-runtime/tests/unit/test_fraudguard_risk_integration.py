"""Unit & Mandatory Security Tests for FraudGuard Risk Integration (Phase 269)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.risk.integrations.fraudguard_risk import FraudGuardRiskIntegrationService
from app.risk.risk_engine import RiskEngine
from app.schemas.fraudguard_api import FraudGuardRiskIntelligenceResponse
from app.schemas.ml_inference import InferenceResult
from app.schemas.ml_risk import FraudProbabilityResult, TransactionRiskResult
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignalType,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_001",
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime.now(UTC),
    )


def test_01_valid_fraud_probability_result_integration() -> None:
    """1. Valid FraudProbabilityResult integration into canonical RiskSignal."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    prob_res = FraudProbabilityResult(
        inference_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        model_id="fraudguard_xgboost",
        model_version="1.0.0",
        fraud_probability=0.85,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
        generated_at=ctx.prediction_timestamp,
    )

    sig = service.integrate_fraud_probability(prob_res, ctx)

    assert sig.signal_type == RiskSignalType.FRAUDGUARD
    assert sig.source == "FRAUDGUARD"
    assert sig.score == 0.85
    assert sig.score_unit == RiskScoreUnit.PROBABILITY
    assert sig.normalized_score == 85.0
    assert sig.source_version == "1.0.0"
    assert sig.source_fingerprint == "r" * 64
    assert sig.metadata["model_id"] == "fraudguard_xgboost"


def test_02_valid_transaction_risk_result_integration() -> None:
    """2. Valid TransactionRiskResult integration into canonical RiskSignal."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    tx_res = TransactionRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.85,
        transaction_risk_score=85.0,
        risk_level="CRITICAL",
        source_inference_id=uuid.uuid4(),
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
        generated_at=ctx.prediction_timestamp,
    )

    sig = service.integrate_transaction_risk_result(tx_res, ctx)

    assert sig.signal_type == RiskSignalType.TRANSACTION
    assert sig.source == "FRAUDGUARD"
    assert sig.score == 85.0
    assert sig.score_unit == RiskScoreUnit.RISK_SCORE
    assert sig.normalized_score == 85.0


def test_03_valid_inference_result_integration() -> None:
    """3. Valid InferenceResult integration preserving model metadata and lineage."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    inf_res = InferenceResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        model_id="fraudguard_xgboost",
        model_version="1.0.0",
        feature_versions={"amount": "1.0.0"},
        prediction_timestamp=ctx.prediction_timestamp,
        fraud_probability=0.35,
        configuration_hash="c" * 64,
        request_fingerprint="req_fp_123",
    )

    sig = service.integrate_inference_result(inf_res, ctx)

    assert sig.signal_type == RiskSignalType.FRAUDGUARD
    assert sig.score == 0.35
    assert sig.normalized_score == 35.0
    assert sig.metadata["model_name"] == "fraudguard_xgboost"
    assert sig.metadata["model_version"] == "1.0.0"


def test_04_cross_tenant_fraudguard_rejection() -> None:
    """4. Mandatory Security Test: Cross-tenant FraudGuard signal fails closed."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    other_tenant = uuid.uuid4()
    prob_res = FraudProbabilityResult(
        inference_id=uuid.uuid4(),
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        model_id="mod",
        model_version="1.0.0",
        fraud_probability=0.85,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
        generated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        service.integrate_fraud_probability(prob_res, ctx)


def test_05_cross_agent_fraudguard_rejection() -> None:
    """5. Mandatory Security Test: Cross-agent FraudGuard signal fails closed."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    other_agent = uuid.uuid4()
    prob_res = FraudProbabilityResult(
        inference_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=other_agent,  # Cross-agent attack!
        transaction_id=ctx.transaction_id,
        model_id="mod",
        model_version="1.0.0",
        fraud_probability=0.85,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
        generated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Agent ID mismatch!"):
        service.integrate_fraud_probability(prob_res, ctx)


def test_06_cross_transaction_fraudguard_rejection() -> None:
    """6. Mandatory Security Test: Cross-transaction FraudGuard signal fails closed."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    prob_res = FraudProbabilityResult(
        inference_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id="tx_other_999",  # Cross-transaction attack!
        model_id="mod",
        model_version="1.0.0",
        fraud_probability=0.85,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
        generated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Transaction ID mismatch!"):
        service.integrate_fraud_probability(prob_res, ctx)


def test_07_invalid_probability_out_of_bounds_rejection() -> None:
    """7. Mandatory Security Test: Invalid probability (> 1 or < 0) fails closed without clamping."""  # noqa: E501
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    with pytest.raises(ValueError):
        prob_res = FraudProbabilityResult(
            inference_id=uuid.uuid4(),
            tenant_id=ctx.tenant_id,
            agent_id=ctx.agent_id,
            transaction_id=ctx.transaction_id,
            model_id="mod",
            model_version="1.0.0",
            fraud_probability=1.5,  # Out of range (> 1.0)!
            configuration_hash="c" * 64,
            source_fingerprint="s" * 64,
            result_fingerprint="r" * 64,
            generated_at=ctx.prediction_timestamp,
        )
        service.integrate_fraud_probability(prob_res, ctx)


def test_08_nan_probability_rejection() -> None:
    """8. Mandatory Security Test: NaN probability fails closed."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    with pytest.raises(ValueError):
        prob_res = FraudProbabilityResult.model_construct(
            inference_id=uuid.uuid4(),
            tenant_id=ctx.tenant_id,
            agent_id=ctx.agent_id,
            transaction_id=ctx.transaction_id,
            model_id="mod",
            model_version="1.0.0",
            fraud_probability=float("nan"),  # NaN!
            configuration_hash="c" * 64,
            source_fingerprint="s" * 64,
            result_fingerprint="r" * 64,
            generated_at=ctx.prediction_timestamp,
        )
        service.integrate_fraud_probability(prob_res, ctx)


def test_09_infinity_probability_rejection() -> None:
    """9. Mandatory Security Test: Infinity probability fails closed."""
    ctx = _make_context()
    service = FraudGuardRiskIntegrationService()

    with pytest.raises(ValueError):
        prob_res = FraudProbabilityResult.model_construct(
            inference_id=uuid.uuid4(),
            tenant_id=ctx.tenant_id,
            agent_id=ctx.agent_id,
            transaction_id=ctx.transaction_id,
            model_id="mod",
            model_version="1.0.0",
            fraud_probability=float("inf"),  # Infinity!
            configuration_hash="c" * 64,
            source_fingerprint="s" * 64,
            result_fingerprint="r" * 64,
            generated_at=ctx.prediction_timestamp,
        )
        service.integrate_fraud_probability(prob_res, ctx)


def test_10_risk_intelligence_response_integration() -> None:
    """10. Test integrating full FraudGuardRiskIntelligenceResponse into RiskEngine."""
    ctx = _make_context()
    adapter = FraudGuardRiskIntegrationService()
    engine = RiskEngine()

    resp = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.70,
        transaction_risk_score=70.0,
        risk_level="HIGH",
        extracted_factors=[],
        policy_decision="ALLOW",
        authoritative=True,
        ml_advisory=True,
        allow_ml_scoring=True,
        result_fingerprint="r" * 64,
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = adapter.integrate_risk_intelligence_response(resp, ctx)
    result = engine.evaluate(ctx, signals)

    assert len(result.normalized_signals) == 2
    assert result.tenant_id == ctx.tenant_id
    assert len(result.result_fingerprint) == 64
