"""Unit & Mandatory Security Tests for Risk Score Calculation (Phase 274)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.integrations.behaviour_risk import BehaviourRiskIntegrationService
from app.risk.integrations.fraudguard_risk import FraudGuardRiskIntegrationService
from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.risk_fusion import RiskFusionEngine
from app.risk.risk_score_calculator import RiskScoreCalculator
from app.schemas.behaviour_risk import BehaviourRiskResult
from app.schemas.fraudguard_api import FraudGuardRiskIntelligenceResponse
from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.risk_engine import (
    RiskEvaluationContext,
    RiskFusionResult,
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


def test_01_composite_advisory_risk_score_calculation() -> None:
    """1. Test composite advisory risk score calculation from fused normalized signals."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()
    calculator = RiskScoreCalculator()

    fraud_adapter = FraudGuardRiskIntegrationService()
    beh_adapter = BehaviourRiskIntegrationService()
    policy_adapter = PolicyRiskIntegrationService()

    fraud_res = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.80,
        transaction_risk_score=80.0,
        risk_level="HIGH",
        extracted_factors=[],
        result_fingerprint="r1" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    beh_res = BehaviourRiskResult(
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        behaviour_risk_score=Decimal("0.40"),
        severity="NORMAL",
        confidence=Decimal("0.90"),
        evaluated_at=ctx.prediction_timestamp,
    )

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
        result_fingerprint="r2" * 32,
    )

    raw_signals: list[RiskSignal] = []
    raw_signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_res, ctx))
    raw_signals.extend(beh_adapter.integrate_behaviour_risk(beh_res, ctx))
    raw_signals.extend(policy_adapter.integrate_policy_risk(policy_res, ctx))

    fused_res = fusion_engine.fuse(ctx, raw_signals)
    calc_res = calculator.calculate_score(fused_res, context=ctx)

    # Weights: FRAUDGUARD=2.0, TRANSACTION=1.5, BEHAVIOUR=1.0. Total = 4.5
    # Scores: FRAUDGUARD=80.0, TRANSACTION=80.0, BEHAVIOUR=40.0
    # Sum = (2.0*80) + (1.5*80) + (1.0*40) = 160 + 120 + 40 = 320. 320 / 4.5 = 71.11111111111111
    assert calc_res.tenant_id == ctx.tenant_id
    assert calc_res.agent_id == ctx.agent_id
    assert calc_res.transaction_id == ctx.transaction_id
    assert calc_res.composite_risk_score > 71.0 and calc_res.composite_risk_score < 72.0
    assert calc_res.policy_precedence == "ALLOW"
    assert len(calc_res.calculation_fingerprint) == 64


def test_02_policy_deny_precedence_preserved_in_score_result() -> None:
    """2. Mandatory Policy Precedence Test: Advisory score DOES NOT override Policy DENY."""
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()
    calculator = RiskScoreCalculator()

    policy_adapter = PolicyRiskIntegrationService()
    fraud_adapter = FraudGuardRiskIntegrationService()

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

    fraud_low = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.05,  # Very low advisory risk!
        transaction_risk_score=5.0,
        risk_level="LOW",
        extracted_factors=[],
        result_fingerprint="r2" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    raw_signals: list[RiskSignal] = []
    raw_signals.extend(policy_adapter.integrate_policy_risk(policy_deny, ctx))
    raw_signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_low, ctx))

    fused_res = fusion_engine.fuse(ctx, raw_signals)
    calc_res = calculator.calculate_score(fused_res, context=ctx)

    assert calc_res.policy_precedence == "DENY"
    # Verification: Result contains advisory score, but NO final decision ALLOW/BLOCK!
    assert not hasattr(calc_res, "final_decision")
    assert not hasattr(calc_res, "allow_decision")


def test_03_confidence_and_decision_excluded_from_scoring_sum() -> None:
    """3. Mandatory Score Unit Test: CONFIDENCE and DECISION signals are excluded from weighted score sum."""  # noqa: E501
    ctx = _make_context()
    calculator = RiskScoreCalculator()
    fusion_engine = RiskFusionEngine()

    conf_sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="BEHAVIOUR",
        score_unit=RiskScoreUnit.CONFIDENCE,
        confidence=0.99,
        normalized_score=None,  # Excluded!
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_c",
    )

    risk_sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="BEHAVIOUR",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=50.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_r",
    )

    fused_res = fusion_engine.fuse(ctx, [conf_sig, risk_sig])
    calc_res = calculator.calculate_score(fused_res, context=ctx)

    assert calc_res.composite_risk_score == 50.0
    assert RiskSignalType.BEHAVIOUR.value in calc_res.included_signal_types


def test_04_target_leakage_rejection_in_calculator() -> None:
    """4. Mandatory Security Test: Target leakage metadata in calculator fails closed."""
    ctx = _make_context()
    calculator = RiskScoreCalculator()

    leak_sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="BEHAVIOUR",
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

    fused_res = RiskFusionResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        signals=[leak_sig],
        signals_by_type={RiskSignalType.BEHAVIOUR.value: [leak_sig]},
        available_signal_types=[RiskSignalType.BEHAVIOUR.value],
        unavailable_signal_types=[],
        policy_signals=[],
        advisory_signals=[leak_sig],
        policy_precedence="NONE",
        source_fingerprints=["fp_leak"],
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )
    with pytest.raises(ValueError, match="Prohibited target leakage"):
        calculator.calculate_score(fused_res, context=ctx)


def test_05_deterministic_replay_calculator() -> None:
    """5. Deterministic Replay Test: Identical inputs produce byte-identical calculation fingerprint."""  # noqa: E501
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()
    calculator = RiskScoreCalculator()

    s1 = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="FRAUDGUARD",
        score=0.30,
        score_unit=RiskScoreUnit.PROBABILITY,
        normalized_score=30.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_1",
    )

    s2 = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="BEHAVIOUR",
        score=40.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=40.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_2",
    )

    fused1 = fusion_engine.fuse(ctx, [s1, s2])
    fused2 = fusion_engine.fuse(ctx, [s2, s1])

    res1 = calculator.calculate_score(fused1, context=ctx)
    res2 = calculator.calculate_score(fused2, context=ctx)

    assert res1.composite_risk_score == res2.composite_risk_score
    assert res1.calculation_fingerprint == res2.calculation_fingerprint


def test_06_phase_boundary_verification() -> None:
    """6. Phase Boundary Verification: RiskScoreCalculationResult MUST NOT contain decision engine fields."""  # noqa: E501
    ctx = _make_context()
    fusion_engine = RiskFusionEngine()
    calculator = RiskScoreCalculator()

    s = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="FRAUDGUARD",
        score=50.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=50.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_1",
    )

    fused = fusion_engine.fuse(ctx, [s])
    calc_res = calculator.calculate_score(fused, context=ctx)

    assert not hasattr(calc_res, "final_decision")
    assert not hasattr(calc_res, "allow_decision")
    assert not hasattr(calc_res, "block_decision")
    assert not hasattr(calc_res, "review_decision")
    assert not hasattr(calc_res, "threshold_config")
