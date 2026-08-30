"""Unit & Mandatory Security Tests for AGENTGUARD Risk Integration (Phase 268)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.integrations.agentguard_risk import AgentGuardRiskIntegrationService
from app.risk.risk_engine import RiskEngine
from app.schemas.agent_risk_profile import AgentRiskProfile
from app.schemas.behaviour_risk import BehaviourRiskResult
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


def test_01_valid_agentguard_risk_profile_integration() -> None:
    """1. Valid AGENTGUARD risk profile integration and signal mapping."""
    ctx = _make_context()
    service = AgentGuardRiskIntegrationService()

    profile = AgentRiskProfile(
        agent_id=ctx.agent_id,
        tenant_id=ctx.tenant_id,
        risk_score=Decimal("0.75"),
        trust_score=Decimal("0.90"),
        risk_level="HIGH",
        recommended_action="REQUIRE_APPROVAL",
        explainable_reasons=["High velocity"],
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = service.integrate_agent_risk_profile(profile, ctx)

    assert len(signals) == 2
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)
    dec_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.DECISION)

    assert risk_sig.signal_type == RiskSignalType.AGENTGUARD
    assert risk_sig.source == "AGENTGUARD"
    assert risk_sig.score == 75.0
    assert risk_sig.normalized_score == 75.0

    assert dec_sig.signal_type == RiskSignalType.AGENTGUARD
    assert dec_sig.decision == "REQUIRE_APPROVAL"
    assert dec_sig.normalized_score is None  # Decision remains categorical!


def test_02_valid_behaviour_risk_result_integration() -> None:
    """2. Valid BehaviourRiskResult integration with separate confidence signal."""
    ctx = _make_context()
    service = AgentGuardRiskIntegrationService()

    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.60"),
        severity="NORMAL",
        confidence=Decimal("0.95"),
        explanation="Normal activity",
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = service.integrate_behaviour_risk_result(beh_res, ctx)

    assert len(signals) == 2
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)
    conf_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.CONFIDENCE)

    assert risk_sig.signal_type == RiskSignalType.BEHAVIOUR
    assert risk_sig.score == 60.0

    assert conf_sig.confidence == 0.95
    assert conf_sig.normalized_score is None  # Confidence is NOT converted to risk score!


def test_03_cross_tenant_agentguard_rejection() -> None:
    """3. Mandatory Security Test: Cross-tenant AGENTGUARD signal fails closed."""
    ctx = _make_context()
    service = AgentGuardRiskIntegrationService()

    other_tenant_id = uuid.uuid4()
    profile = AgentRiskProfile(
        agent_id=ctx.agent_id,
        tenant_id=other_tenant_id,  # Cross-tenant attack!
        risk_score=Decimal("0.30"),
        trust_score=Decimal("0.90"),
        risk_level="LOW",
        evaluated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        service.integrate_agent_risk_profile(profile, ctx)


def test_04_cross_agent_agentguard_rejection() -> None:
    """4. Mandatory Security Test: Cross-agent AGENTGUARD signal fails closed."""
    ctx = _make_context()
    service = AgentGuardRiskIntegrationService()

    other_agent_id = uuid.uuid4()
    profile = AgentRiskProfile(
        agent_id=other_agent_id,  # Cross-agent attack!
        tenant_id=ctx.tenant_id,
        risk_score=Decimal("0.30"),
        trust_score=Decimal("0.90"),
        risk_level="LOW",
        evaluated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Agent ID mismatch!"):
        service.integrate_agent_risk_profile(profile, ctx)


def test_05_future_timestamp_agentguard_rejection() -> None:
    """5. Mandatory Security Test: Future timestamp AGENTGUARD signal fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    service = AgentGuardRiskIntegrationService()

    profile = AgentRiskProfile(
        agent_id=ctx.agent_id,
        tenant_id=ctx.tenant_id,
        risk_score=Decimal("0.30"),
        trust_score=Decimal("0.90"),
        risk_level="LOW",
        evaluated_at=future_ts,  # Future timestamp!
    )

    with pytest.raises(ValueError, match="future relative to prediction timestamp"):
        service.integrate_agent_risk_profile(profile, ctx)


def test_06_cold_start_preservation() -> None:
    """6. Cold-start preservation in AGENTGUARD signal."""
    ctx = _make_context()
    service = AgentGuardRiskIntegrationService()

    profile = AgentRiskProfile(
        agent_id=ctx.agent_id,
        tenant_id=ctx.tenant_id,
        risk_score=Decimal("0.50"),
        trust_score=Decimal("0.50"),
        risk_level="COLD_START",
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = service.integrate_agent_risk_profile(profile, ctx)
    risk_sig = next(s for s in signals if s.score_unit == RiskScoreUnit.RISK_SCORE)

    assert risk_sig.cold_start is True


def test_07_target_leakage_rejection_in_metadata() -> None:
    """7. Target leakage rejection in AGENTGUARD metadata."""
    ctx = _make_context()
    service = AgentGuardRiskIntegrationService()

    profile = AgentRiskProfile(
        agent_id=ctx.agent_id,
        tenant_id=ctx.tenant_id,
        risk_score=Decimal("0.50"),
        trust_score=Decimal("0.50"),
        risk_level="LOW",
        explainable_reasons=["is_fraud_confirmed"],  # Data leakage!
        evaluated_at=ctx.prediction_timestamp,
    )

    with pytest.raises(ValueError, match="Prohibited target leakage"):
        service.integrate_agent_risk_profile(profile, ctx)


def test_08_integration_with_risk_engine() -> None:
    """8. Integration test with RiskEngine architecture (Phases 266-268)."""
    ctx = _make_context()
    adapter = AgentGuardRiskIntegrationService()
    engine = RiskEngine()

    profile = AgentRiskProfile(
        agent_id=ctx.agent_id,
        tenant_id=ctx.tenant_id,
        risk_score=Decimal("0.40"),
        trust_score=Decimal("0.80"),
        risk_level="NORMAL",
        recommended_action="ALLOW",
        evaluated_at=ctx.prediction_timestamp,
    )

    signals = adapter.integrate_agent_risk_profile(profile, ctx)
    result = engine.evaluate(ctx, signals)

    assert result.tenant_id == ctx.tenant_id
    assert len(result.normalized_signals) == 2
    assert len(result.result_fingerprint) == 64
