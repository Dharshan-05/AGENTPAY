"""Unit & Mandatory Security Tests for Behaviour Risk Integration (Phase 270)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.integrations.behaviour_risk import BehaviourRiskIntegrationService
from app.risk.risk_engine import RiskEngine
from app.schemas.behaviour_risk import BehaviourRiskResult
from app.schemas.ml_risk import MLBehaviourRiskResult
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


def test_01_valid_behaviour_risk_mapping() -> None:
    """1. Valid Behaviour risk mapping into RiskSignal objects."""
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.65"),
        severity="MEDIUM",
        confidence=Decimal("0.90"),
        explanation="Moderate deviation",
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = service.integrate_behaviour_risk(beh_res, ctx)

    assert len(signals) == 3
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)
    conf_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.CONFIDENCE)
    dec_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.DECISION)

    assert risk_sig.signal_type == RiskSignalType.BEHAVIOUR
    assert risk_sig.score == 65.0
    assert risk_sig.normalized_score == 65.0

    assert conf_sig.confidence == 0.90
    assert conf_sig.normalized_score is None  # Confidence is NOT converted to risk score!

    assert dec_sig.decision == "MEDIUM"
    assert dec_sig.normalized_score is None  # Decisions remain categorical!


def test_02_ml_behaviour_risk_result_mapping() -> None:
    """2. Valid MLBehaviourRiskResult mapping with cold-start preservation."""
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    ml_beh = MLBehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        behaviour_risk_score=75.0,
        behaviour_confidence=0.85,
        is_cold_start=True,
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    signals = service.integrate_behaviour_risk(ml_beh, ctx)

    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)
    assert risk_sig.cold_start is True
    assert risk_sig.score == 75.0


def test_03_cross_tenant_behaviour_rejection() -> None:
    """3. Mandatory Security Test: Cross-tenant Behaviour signal fails closed."""
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    other_tenant = uuid.uuid4()
    beh_res = BehaviourRiskResult(
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.50"),
        severity="NORMAL",
        confidence=Decimal("0.80"),
        evaluated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        service.integrate_behaviour_risk(beh_res, ctx)


def test_04_cross_agent_behaviour_rejection() -> None:
    """4. Mandatory Security Test: Cross-agent Behaviour signal fails closed."""
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    other_agent = uuid.uuid4()
    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=other_agent,  # Cross-agent attack!
        behaviour_risk_score=Decimal("0.50"),
        severity="NORMAL",
        confidence=Decimal("0.80"),
        evaluated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Agent ID mismatch!"):
        service.integrate_behaviour_risk(beh_res, ctx)


def test_05_future_timestamp_behaviour_rejection() -> None:
    """5. Mandatory Security Test: Future timestamp Behaviour signal fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    service = BehaviourRiskIntegrationService()

    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.50"),
        severity="NORMAL",
        confidence=Decimal("0.80"),
        evaluated_at=future_ts,  # Future timestamp!
    )

    with pytest.raises(ValueError, match="future relative to prediction timestamp"):
        service.integrate_behaviour_risk(beh_res, ctx)


def test_06_behaviour_risk_score_out_of_bounds_rejection() -> None:
    """6. Mandatory Security Test: Invalid behaviour risk score (> 100 or < 0) fails closed."""  # noqa: E501
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    with pytest.raises(ValueError):
        payload = {
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "transaction_id": ctx.transaction_id,
            "behaviour_risk_score": 150.0,  # Out of range!
            "signal_timestamp": ctx.prediction_timestamp,
        }
        service.integrate_behaviour_risk(payload, ctx)


def test_07_nan_confidence_behaviour_rejection() -> None:
    """7. Mandatory Security Test: NaN confidence fails closed."""
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    with pytest.raises(ValueError, match="NaN or Infinity"):
        payload = {
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "transaction_id": ctx.transaction_id,
            "behaviour_risk_score": 50.0,
            "confidence": float("nan"),  # NaN!
            "signal_timestamp": ctx.prediction_timestamp,
        }
        service.integrate_behaviour_risk(payload, ctx)


def test_08_target_leakage_rejection() -> None:
    """8. Mandatory Security Test: Target leakage in Behaviour metadata fails closed."""
    ctx = _make_context()
    service = BehaviourRiskIntegrationService()

    with pytest.raises(ValueError, match="Prohibited target leakage"):
        payload = {
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "transaction_id": ctx.transaction_id,
            "behaviour_risk_score": 50.0,
            "signal_timestamp": ctx.prediction_timestamp,
            "metadata": {"is_fraud": True},  # Data leakage!
        }
        service.integrate_behaviour_risk(payload, ctx)


def test_09_behaviour_risk_engine_integration() -> None:
    """9. Integration test: Behaviour signals pass through RiskEngine cleanly."""
    ctx = _make_context()
    adapter = BehaviourRiskIntegrationService()
    engine = RiskEngine()

    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.40"),
        severity="LOW",
        confidence=Decimal("0.90"),
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = adapter.integrate_behaviour_risk(beh_res, ctx)
    result = engine.evaluate(ctx, signals)

    assert result.tenant_id == ctx.tenant_id
    assert len(result.normalized_signals) == 3
    assert len(result.result_fingerprint) == 64
