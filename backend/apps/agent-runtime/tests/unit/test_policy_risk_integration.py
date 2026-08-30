"""Unit & Mandatory Security Tests for Policy Risk Integration (Phase 272)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.risk_engine import RiskEngine
from app.schemas.ml_risk import PolicyRiskResult
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


def test_01_valid_policy_allow_mapping() -> None:
    """1. Valid POLICY ALLOW signal mapping."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=10.0,
        policy_decision="ALLOW",
        policy_decision_code="POLICY_ALLOW_PASSED",
        authoritative=True,
        allow_ml_scoring=True,
        source="AGENTGUARD_POLICY_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = service.integrate_policy_risk(policy_res, ctx)

    assert len(signals) == 2
    dec_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.DECISION)
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)

    assert dec_sig.signal_type == RiskSignalType.POLICY
    assert dec_sig.decision == "ALLOW"
    assert dec_sig.normalized_score is None  # Decision is NOT converted to numeric risk score!
    assert dec_sig.metadata["policy_authoritative"] is True

    assert risk_sig.score == 10.0
    assert risk_sig.normalized_score == 10.0


def test_02_valid_policy_deny_mapping() -> None:
    """2. Valid POLICY DENY signal mapping preserving policy precedence metadata."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=100.0,
        policy_decision="DENY",
        policy_decision_code="POLICY_DENY_RESTRICTED",
        authoritative=True,
        allow_ml_scoring=False,
        source="AGENTGUARD_POLICY_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = service.integrate_policy_risk(policy_res, ctx)

    dec_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.DECISION)
    assert dec_sig.decision == "DENY"
    assert dec_sig.metadata["allow_ml_scoring"] is False
    assert dec_sig.metadata["policy_override_forbidden"] is True


def test_03_valid_policy_review_mapping() -> None:
    """3. Valid POLICY REQUIRE_APPROVAL / REVIEW signal mapping."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=50.0,
        policy_decision="REQUIRE_APPROVAL",
        policy_decision_code="POLICY_APPROVAL_REQUIRED",
        authoritative=True,
        allow_ml_scoring=True,
        source="AGENTGUARD_POLICY_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = service.integrate_policy_risk(policy_res, ctx)
    dec_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.DECISION)

    assert dec_sig.decision == "REQUIRE_APPROVAL"


def test_04_unknown_policy_decision_rejection() -> None:
    """4. Mandatory Security Test: UNKNOWN policy decision fails closed."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=50.0,
        policy_decision="UNKNOWN",  # Unknown decision!
        policy_decision_code="UNKNOWN_POLICY",
        authoritative=True,
        allow_ml_scoring=True,
        source="AGENTGUARD_POLICY_ENGINE",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="UNKNOWN policy decision"):
        service.integrate_policy_risk(policy_res, ctx)


def test_05_cross_tenant_policy_rejection() -> None:
    """5. Mandatory Security Test: Cross-tenant Policy signal fails closed."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    other_tenant = uuid.uuid4()
    policy_res = PolicyRiskResult(
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        service.integrate_policy_risk(policy_res, ctx)


def test_06_cross_agent_policy_rejection() -> None:
    """6. Mandatory Security Test: Cross-agent Policy signal fails closed."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    other_agent = uuid.uuid4()
    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=other_agent,  # Cross-agent attack!
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Agent ID mismatch!"):
        service.integrate_policy_risk(policy_res, ctx)


def test_07_future_timestamp_policy_rejection() -> None:
    """7. Mandatory Security Test: Future timestamp Policy signal fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    service = PolicyRiskIntegrationService()

    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=future_ts,  # Future timestamp!
        prediction_timestamp=now,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    with pytest.raises(ValueError, match="Point-in-Time violation"):
        service.integrate_policy_risk(policy_res, ctx)


def test_08_target_leakage_rejection() -> None:
    """8. Mandatory Security Test: Target leakage in Policy metadata fails closed."""
    ctx = _make_context()
    service = PolicyRiskIntegrationService()

    with pytest.raises(ValueError, match="Prohibited target leakage"):
        payload = {
            "tenant_id": ctx.tenant_id,
            "agent_id": ctx.agent_id,
            "transaction_id": ctx.transaction_id,
            "policy_decision": "ALLOW",
            "signal_timestamp": ctx.prediction_timestamp,
            "metadata": {"investigation_result": "FRAUD_CONFIRMED"},  # Data leakage!
        }
        service.integrate_policy_risk(payload, ctx)


def test_09_policy_risk_engine_integration() -> None:
    """9. Integration test: Policy signals pass through RiskEngine cleanly."""
    ctx = _make_context()
    adapter = PolicyRiskIntegrationService()
    engine = RiskEngine()

    policy_res = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=0.0,
        policy_decision="ALLOW",
        policy_decision_code="PASS",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s" * 64,
        result_fingerprint="r" * 64,
    )

    signals = adapter.integrate_policy_risk(policy_res, ctx)
    result = engine.evaluate(ctx, signals)

    assert result.tenant_id == ctx.tenant_id
    assert len(result.normalized_signals) == 2
    assert len(result.result_fingerprint) == 64
