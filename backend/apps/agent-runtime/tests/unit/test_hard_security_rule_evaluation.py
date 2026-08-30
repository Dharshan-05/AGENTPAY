"""Unit & Mandatory Security Tests for Hard Security Rule Evaluation Engine (Phase 277)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.risk.hard_security_rules import HardSecurityRulesEngine
from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.risk_fusion import RiskFusionEngine
from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.risk_engine import (
    HardSecurityRuleOutcome,
    HardSecurityRuleSeverity,
    HardSecurityRuleType,
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


def test_01_all_rules_passing() -> None:
    """1. Test evaluation when all security rules pass cleanly."""
    ctx = _make_context()
    engine = HardSecurityRulesEngine()

    sig = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="FRAUDGUARD",
        score=0.10,
        score_unit=RiskScoreUnit.PROBABILITY,
        normalized_score=10.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_1",
    )

    fusion_engine = RiskFusionEngine()
    fused_res = fusion_engine.fuse(ctx, [sig])

    eval_res = engine.evaluate_rules(ctx, [sig], fused_result=fused_res)

    assert eval_res.tenant_id == ctx.tenant_id
    assert eval_res.has_triggered_rules is False
    assert len(eval_res.triggered_rules) == 0
    assert eval_res.max_triggered_severity is None
    assert len(eval_res.result_fingerprint) == 64


def test_02_policy_deny_rule_triggering() -> None:
    """2. Mandatory Security Test: Rule HSR-001 triggers on Policy DENY precedence."""
    ctx = _make_context()
    engine = HardSecurityRulesEngine()
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

    eval_res = engine.evaluate_rules(ctx, signals, fused_result=fused_res)

    assert eval_res.has_triggered_rules is True
    hsr_001 = next(r for r in eval_res.triggered_rules if r.rule_id == "HSR-001")
    assert hsr_001.rule_type == HardSecurityRuleType.POLICY_DENY
    assert hsr_001.severity == HardSecurityRuleSeverity.CRITICAL
    assert hsr_001.outcome == HardSecurityRuleOutcome.TRIGGERED
    assert hsr_001.requires_security_intervention is True
    assert eval_res.max_triggered_severity == HardSecurityRuleSeverity.CRITICAL


def test_03_identity_mismatch_rule_triggering() -> None:
    """3. Mandatory Security Test: Rule HSR-003 triggers on identity mismatch."""
    ctx = _make_context()
    engine = HardSecurityRulesEngine()

    other_tenant = uuid.uuid4()
    bad_sig = RiskSignal(
        signal_type=RiskSignalType.BEHAVIOUR,
        source="BEHAVIOUR",
        score=10.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=10.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_bad",
    )

    eval_res = engine.evaluate_rules(ctx, [bad_sig])

    assert eval_res.has_triggered_rules is True
    trig_rule = next(r for r in eval_res.triggered_rules if r.rule_id == "HSR-003")
    assert trig_rule.rule_type == HardSecurityRuleType.IDENTITY_MISMATCH
    assert trig_rule.severity == HardSecurityRuleSeverity.CRITICAL


def test_04_future_timestamp_rule_triggering() -> None:
    """4. Mandatory Security Test: Rule HSR-004 triggers on future timestamp."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_ts = datetime(2030, 1, 1, tzinfo=UTC)
    engine = HardSecurityRulesEngine()

    future_sig = RiskSignal(
        signal_type=RiskSignalType.INTENT,
        source="INTENT",
        score=10.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=10.0,
        timestamp=future_ts,  # Future timestamp!
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_fut",
    )

    eval_res = engine.evaluate_rules(ctx, [future_sig])

    assert eval_res.has_triggered_rules is True
    trig_rule = next(r for r in eval_res.triggered_rules if r.rule_id == "HSR-004")
    assert trig_rule.rule_type == HardSecurityRuleType.FUTURE_TIMESTAMP
    assert trig_rule.severity == HardSecurityRuleSeverity.HIGH


def test_05_target_leakage_rule_triggering() -> None:
    """5. Mandatory Security Test: Rule HSR-005 triggers on prohibited target leakage metadata."""
    ctx = _make_context()
    engine = HardSecurityRulesEngine()

    leak_sig = RiskSignal(
        signal_type=RiskSignalType.TRANSACTION,
        source="FRAUDGUARD",
        score=20.0,
        score_unit=RiskScoreUnit.RISK_SCORE,
        normalized_score=20.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_leak",
        metadata={"is_fraud": True},  # Data leakage!
    )

    eval_res = engine.evaluate_rules(ctx, [leak_sig])

    assert eval_res.has_triggered_rules is True
    trig_rule = next(r for r in eval_res.triggered_rules if r.rule_id == "HSR-005")
    assert trig_rule.rule_type == HardSecurityRuleType.TARGET_LEAKAGE
    assert trig_rule.severity == HardSecurityRuleSeverity.CRITICAL


def test_06_deterministic_rule_evaluation_sorting_and_replay() -> None:
    """6. Deterministic Sorting & Replay: Primary severity desc, secondary rule_id asc."""
    ctx = _make_context()
    engine = HardSecurityRulesEngine()

    s = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="FRAUDGUARD",
        score=10.0,
        score_unit=RiskScoreUnit.PROBABILITY,
        normalized_score=10.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_1",
    )

    res1 = engine.evaluate_rules(ctx, [s])
    res2 = engine.evaluate_rules(ctx, [s])

    assert res1.result_fingerprint == res2.result_fingerprint

    # Verify severity ordering: CRITICAL rules come before HIGH rules
    severities = [SEVERITY_ORDER_TEST(e.severity) for e in res1.evaluations]
    assert sorted(severities, reverse=True) == severities


def SEVERITY_ORDER_TEST(sev: HardSecurityRuleSeverity) -> int:
    order = {
        HardSecurityRuleSeverity.CRITICAL: 4,
        HardSecurityRuleSeverity.HIGH: 3,
        HardSecurityRuleSeverity.MEDIUM: 2,
        HardSecurityRuleSeverity.LOW: 1,
    }
    return order[sev]


def test_07_phase_boundary_verification() -> None:
    """7. Mandatory Phase Boundary Test: HardSecurityEvaluationResult MUST NOT contain final authorization decisions."""  # noqa: E501
    ctx = _make_context()
    engine = HardSecurityRulesEngine()

    sig = RiskSignal(
        signal_type=RiskSignalType.FRAUDGUARD,
        source="FRAUDGUARD",
        score=0.99,
        score_unit=RiskScoreUnit.PROBABILITY,
        normalized_score=99.0,
        timestamp=ctx.prediction_timestamp,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        source_fingerprint="fp_1",
    )

    eval_res = engine.evaluate_rules(ctx, [sig])

    assert not hasattr(eval_res, "final_decision")
    assert not hasattr(eval_res, "allow_decision")
    assert not hasattr(eval_res, "block_decision")
    assert not hasattr(eval_res, "review_decision")
    assert not hasattr(eval_res, "authorization_status")
