"""Unit & Mandatory Security Tests for Intent Risk Integration (Phase 271)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.risk.integrations.intent_risk import IntentRiskIntegrationService
from app.risk.risk_engine import RiskEngine
from app.schemas.ml_risk import IntentRiskResult
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


def test_01_valid_intent_risk_mapping() -> None:
    """1. Valid IntentRiskResult mapping into canonical RiskSignal objects."""
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        intent_risk_score=35.0,
        intent_confidence=0.92,
        intent_can_proceed=True,
        intent_decision="VERIFIED",
        is_available=True,
        source="AGENTGUARD_INTENT_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = service.integrate_intent_risk(intent_res, ctx)

    assert len(signals) == 3
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)
    conf_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.CONFIDENCE)
    dec_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.DECISION)

    assert risk_sig.signal_type == RiskSignalType.INTENT
    assert risk_sig.score == 35.0
    assert risk_sig.normalized_score == 35.0
    assert risk_sig.metadata["intent_can_proceed"] is True

    assert conf_sig.confidence == 0.92
    assert conf_sig.normalized_score is None  # Confidence is NOT converted to risk score!

    assert dec_sig.decision == "VERIFIED"
    assert dec_sig.normalized_score is None  # Decisions remain categorical!


def test_02_intent_can_proceed_does_not_zero_out_risk() -> None:
    """2. Mandatory Security Test: intent_can_proceed=True does NOT zero out risk or grant ALLOW."""  # noqa: E501
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        intent_risk_score=80.0,  # High risk score!
        intent_confidence=0.90,
        intent_can_proceed=True,  # Upstream recommendation flag
        intent_decision="VERIFIED",
        is_available=True,
        source="AGENTGUARD_INTENT_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = service.integrate_intent_risk(intent_res, ctx)
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)

    assert risk_sig.score == 80.0
    assert risk_sig.normalized_score == 80.0  # Risk score remains 80.0, NOT zeroed out!


def test_03_cross_tenant_intent_rejection() -> None:
    """3. Mandatory Security Test: Cross-tenant Intent signal fails closed."""
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    other_tenant = uuid.uuid4()
    intent_res = IntentRiskResult(
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        intent_risk_score=20.0,
        intent_confidence=0.90,
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        service.integrate_intent_risk(intent_res, ctx)


def test_04_cross_agent_intent_rejection() -> None:
    """4. Mandatory Security Test: Cross-agent Intent signal fails closed."""
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    other_agent = uuid.uuid4()
    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=other_agent,  # Cross-agent attack!
        transaction_id=ctx.transaction_id,
        intent_risk_score=20.0,
        intent_confidence=0.90,
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Agent ID mismatch!"):
        service.integrate_intent_risk(intent_res, ctx)


def test_05_cross_transaction_intent_rejection() -> None:
    """5. Mandatory Security Test: Cross-transaction Intent signal fails closed."""
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id="tx_other_999",  # Cross-transaction attack!
        intent_risk_score=20.0,
        intent_confidence=0.90,
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Transaction ID mismatch!"):
        service.integrate_intent_risk(intent_res, ctx)


def test_06_future_timestamp_intent_rejection() -> None:
    """6. Mandatory Security Test: Future timestamp Intent signal fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    service = IntentRiskIntegrationService()

    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        intent_risk_score=20.0,
        intent_confidence=0.90,
        signal_timestamp=future_ts,  # Future timestamp!
        prediction_timestamp=now,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="future relative to prediction timestamp"):
        service.integrate_intent_risk(intent_res, ctx)


def test_07_intent_risk_score_out_of_bounds_rejection() -> None:
    """7. Mandatory Security Test: Invalid intent risk score (> 100 or < 0) fails closed."""
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    with pytest.raises(ValueError):
        payload = {
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "transaction_id": ctx.transaction_id,
            "intent_risk_score": -10.0,  # Negative score!
            "signal_timestamp": ctx.prediction_timestamp,
        }
        service.integrate_intent_risk(payload, ctx)


def test_08_target_leakage_rejection() -> None:
    """8. Mandatory Security Test: Target leakage in Intent metadata fails closed."""
    ctx = _make_context()
    service = IntentRiskIntegrationService()

    with pytest.raises(ValueError, match="Prohibited target leakage"):
        payload = {
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "transaction_id": ctx.transaction_id,
            "intent_risk_score": 30.0,
            "signal_timestamp": ctx.prediction_timestamp,
            "metadata": {"chargeback_result": "SUCCESS"},  # Data leakage!
        }
        service.integrate_intent_risk(payload, ctx)


def test_09_intent_risk_engine_integration() -> None:
    """9. Integration test: Intent signals pass through RiskEngine cleanly."""
    ctx = _make_context()
    adapter = IntentRiskIntegrationService()
    engine = RiskEngine()

    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        intent_risk_score=25.0,
        intent_confidence=0.95,
        intent_can_proceed=True,
        intent_decision="VERIFIED",
        is_available=True,
        source="AGENTGUARD_INTENT_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = adapter.integrate_intent_risk(intent_res, ctx)
    result = engine.evaluate(ctx, signals)

    assert result.tenant_id == ctx.tenant_id
    assert len(result.normalized_signals) == 3
    assert len(result.result_fingerprint) == 64
