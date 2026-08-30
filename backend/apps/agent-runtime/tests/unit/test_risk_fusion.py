"""Unit & Mandatory Security Tests for Risk Fusion Engine (Phase 273)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.integrations.behaviour_risk import BehaviourRiskIntegrationService
from app.risk.integrations.fraudguard_risk import FraudGuardRiskIntegrationService
from app.risk.integrations.intent_risk import IntentRiskIntegrationService
from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.risk_fusion import RiskFusionEngine
from app.schemas.behaviour_risk import BehaviourRiskResult
from app.schemas.fraudguard_api import FraudGuardRiskIntelligenceResponse
from app.schemas.ml_risk import IntentRiskResult, PolicyRiskResult
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskScoreUnit,
    RiskSignal,
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


def test_01_multi_source_risk_fusion() -> None:
    """1. Test multi-source risk signal fusion across POLICY, FRAUDGUARD, BEHAVIOUR, INTENT."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    policy_adapter = PolicyRiskIntegrationService()
    fraud_adapter = FraudGuardRiskIntegrationService()
    beh_adapter = BehaviourRiskIntegrationService()
    intent_adapter = IntentRiskIntegrationService()

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
        source_fingerprint="s1" * 32,
        result_fingerprint="r1" * 32,
    )

    fraud_res = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.25,
        transaction_risk_score=25.0,
        risk_level="LOW",
        extracted_factors=[],
        result_fingerprint="r2" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.30"),
        severity="NORMAL",
        confidence=Decimal("0.95"),
        evaluated_at=ctx.prediction_timestamp,
    )

    intent_res = IntentRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        intent_risk_score=20.0,
        intent_confidence=0.90,
        intent_can_proceed=True,
        intent_decision="VERIFIED",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s3" * 32,
        result_fingerprint="r3" * 32,
    )

    raw_signals: list[RiskSignal] = []
    raw_signals.extend(policy_adapter.integrate_policy_risk(policy_res, ctx))
    raw_signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_res, ctx))
    raw_signals.extend(beh_adapter.integrate_behaviour_risk(beh_res, ctx))
    raw_signals.extend(intent_adapter.integrate_intent_risk(intent_res, ctx))

    fused_res = fusion_engine.fuse(ctx, raw_signals)

    assert fused_res.tenant_id == ctx.tenant_id
    assert fused_res.agent_id == ctx.agent_id
    assert fused_res.transaction_id == ctx.transaction_id
    assert len(fused_res.signals) > 0
    assert len(fused_res.policy_signals) == 2
    assert len(fused_res.advisory_signals) == len(fused_res.signals) - 2
    assert fused_res.policy_precedence == "ALLOW"
    assert len(fused_res.result_fingerprint) == 64


def test_02_policy_deny_precedence_in_fusion() -> None:
    """2. Mandatory Policy Precedence Test: Policy DENY establishes DENY precedence."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    policy_adapter = PolicyRiskIntegrationService()
    policy_deny = PolicyRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        policy_risk_score=100.0,
        policy_decision="DENY",
        policy_decision_code="DENIED",
        signal_timestamp=ctx.prediction_timestamp,
        prediction_timestamp=ctx.prediction_timestamp,
        configuration_hash="c" * 64,
        source_fingerprint="s1" * 32,
        result_fingerprint="r1" * 32,
    )

    signals = policy_adapter.integrate_policy_risk(policy_deny, ctx)
    fused_res = fusion_engine.fuse(ctx, signals)

    assert fused_res.policy_precedence == "DENY"
    # Verification: Fused result is an immutable representation without decision engine fields!
    assert not hasattr(fused_res, "final_decision")
    assert not hasattr(fused_res, "decision_allow")


def test_03_conflicting_policy_decisions_rejection() -> None:
    """3. Mandatory Security Test: Conflicting policy decisions (ALLOW + DENY) fail closed."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    s1 = RiskSignal(
        signal_type=RiskSignalType.POLICY,
        source="POLICY_A",
        score_unit=RiskScoreUnit.DECISION,
        decision="ALLOW",
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_version="1.0.0",
        source_fingerprint="fp_1",
    )

    s2 = RiskSignal(
        signal_type=RiskSignalType.POLICY,
        source="POLICY_B",
        score_unit=RiskScoreUnit.DECISION,
        decision="DENY",
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_version="1.0.0",
        source_fingerprint="fp_2",
    )

    with pytest.raises(ValueError, match="Conflicting policy decisions"):
        fusion_engine.fuse(ctx, [s1, s2])


def test_04_cross_tenant_signal_injection_rejection() -> None:
    """4. Mandatory Security Test: Cross-tenant signal in fusion fails closed."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    other_tenant = uuid.uuid4()
    foreign_signal = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="BEHAVIOUR",
        score=20.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=20.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=other_tenant,  # Foreign tenant!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_other",
    )

    with pytest.raises(ValueError, match="Tenant ID mismatch!"):
        fusion_engine.fuse(ctx, [foreign_signal])


def test_05_future_timestamp_signal_rejection() -> None:
    """5. Mandatory Security Test: Future timestamp signal in fusion fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    fusion_engine = RiskFusionEngine()

    future_signal = RiskSignal(
        signal_type=RiskSignalType.INTENT,
        source="INTENT",
        score=20.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=20.0,
        timestamp=future_ts,  # Future timestamp!
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_future",
    )

    with pytest.raises(ValueError, match="future relative to prediction timestamp"):
        fusion_engine.fuse(ctx, [future_signal])


def test_06_target_leakage_rejection_in_fusion() -> None:
    """6. Mandatory Security Test: Target leakage metadata in fusion fails closed."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    leakage_signal = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="FRAUDGUARD",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=50.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_leak",
        metadata={"is_fraud": True},  # Data leakage!
    )

    with pytest.raises(ValueError, match="Prohibited target leakage"):
        fusion_engine.fuse(ctx, [leakage_signal])


def test_07_deterministic_replay_fusion() -> None:
    """7. Deterministic Replay: Identical input context & signals produce identical result fingerprint."""  # noqa: E501
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    s1 = RiskSignal(
        signal_type=RiskSignalType.POLICY,
        source="AGENTGUARD_POLICY",
        score_unit=RiskScoreUnit.DECISION,
        decision="ALLOW",
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_version="1.0.0",
        source_fingerprint="fp_01",
    )

    s2 = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="FRAUDGUARD_XGBOOST",
        score=0.15,
        score_unit=RiskScoreUnit.PROBABILITY,
        normalized_score=15.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_version="1.0.0",
        source_fingerprint="fp_02",
    )

    res1 = fusion_engine.fuse(ctx, [s1, s2])
    res2 = fusion_engine.fuse(ctx, [s2, s1])  # Reverse input order

    assert res1.result_fingerprint == res2.result_fingerprint
    assert res1.configuration_hash == res2.configuration_hash


def test_08_phase_boundary_verification() -> None:
    """8. Phase Boundary Verification: RiskFusionResult MUST NOT contain decision engine / weighting fields."""  # noqa: E501
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()

    s = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="FRAUDGUARD",
        score=0.20,
        score_unit=RiskScoreUnit.PROBABILITY,
        normalized_score=20.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_01",
    )

    fused = fusion_engine.fuse(ctx, [s])

    # Absolute rule verification
    assert not hasattr(fused, "final_decision")
    assert not hasattr(fused, "weighted_risk_score")
    assert not hasattr(fused, "allow_decision")
    assert not hasattr(fused, "block_decision")
    assert not hasattr(fused, "review_decision")
    assert not hasattr(fused, "threshold_config")
