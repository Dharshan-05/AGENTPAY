"""Unit & Mandatory Security Tests for ALLOW Decision Engine (Phase 278)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.risk.decisions.allow_decision import AllowDecisionEngine
from app.schemas.risk_engine import (
    HardSecurityEvaluationResult,
    HardSecurityRuleEvaluation,
    HardSecurityRuleOutcome,
    HardSecurityRuleSeverity,
    HardSecurityRuleType,
    RiskEvaluationContext,
    RiskScoreCalculationResult,
    RiskScoreUnit,
    RiskThresholdBand,
    RiskThresholdEvaluationResult,
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


def test_01_clean_low_risk_allow_qualification() -> None:
    """1. Test clean LOW risk evaluation qualifies for ALLOW."""
    ctx = _make_context()
    engine = AllowDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=15.0,
        composite_risk_score_decimal=Decimal("15.0"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        included_signal_types=["FRAUDGUARD"],
        excluded_signal_types=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        applied_weights={"FRAUDGUARD": 2.0},
        total_applied_weight=2.0,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["fp_1"],
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
    )

    thresh_res = RiskThresholdEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        risk_score=15.0,
        risk_score_decimal=Decimal("15.0"),
        classification="LOW",
        matched_threshold_band=RiskThresholdBand.LOW_RISK_BAND,
        configuration_version="1.0.0",
        configuration_hash="t" * 64,
        evaluation_fingerprint="tf" * 32,
    )

    sec_res = HardSecurityEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        evaluations=[],
        triggered_rules=[],
        has_triggered_rules=False,
        max_triggered_severity=None,
        policy_precedence="ALLOW",
        configuration_hash="h" * 64,
        result_fingerprint="rf" * 32,
    )

    is_allow, reasons = engine.evaluate_allow(ctx, calc_res, thresh_res, sec_res)

    assert is_allow is True
    assert "LOW_RISK_ALLOW_CLEAN" in reasons


def test_02_policy_deny_disqualifies_allow() -> None:
    """2. Mandatory Security Test: Policy DENY makes ALLOW impossible."""
    ctx = _make_context()
    engine = AllowDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=15.0,
        composite_risk_score_decimal=Decimal("15.0"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        included_signal_types=["FRAUDGUARD"],
        excluded_signal_types=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        applied_weights={"FRAUDGUARD": 2.0},
        total_applied_weight=2.0,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["fp_1"],
        policy_precedence="DENY",  # Policy DENY!
        calculation_fingerprint="c" * 64,
    )

    thresh_res = RiskThresholdEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        risk_score=15.0,
        risk_score_decimal=Decimal("15.0"),
        classification="LOW",
        matched_threshold_band=RiskThresholdBand.LOW_RISK_BAND,
        configuration_version="1.0.0",
        configuration_hash="t" * 64,
        evaluation_fingerprint="tf" * 32,
    )

    sec_res = HardSecurityEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        evaluations=[],
        triggered_rules=[],
        has_triggered_rules=False,
        max_triggered_severity=None,
        policy_precedence="DENY",
        configuration_hash="h" * 64,
        result_fingerprint="rf" * 32,
    )

    is_allow, reasons = engine.evaluate_allow(ctx, calc_res, thresh_res, sec_res)

    assert is_allow is False
    assert "POLICY_DENY_RESTRICTION" in reasons


def test_03_triggered_security_rule_disqualifies_allow() -> None:
    """3. Mandatory Security Test: Triggered hard security rule disqualifies ALLOW."""
    ctx = _make_context()
    engine = AllowDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=10.0,
        composite_risk_score_decimal=Decimal("10.0"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        included_signal_types=["FRAUDGUARD"],
        excluded_signal_types=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        applied_weights={"FRAUDGUARD": 2.0},
        total_applied_weight=2.0,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["fp_1"],
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
    )

    thresh_res = RiskThresholdEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        risk_score=10.0,
        risk_score_decimal=Decimal("10.0"),
        classification="LOW",
        matched_threshold_band=RiskThresholdBand.LOW_RISK_BAND,
        configuration_version="1.0.0",
        configuration_hash="t" * 64,
        evaluation_fingerprint="tf" * 32,
    )

    trig_rule = HardSecurityRuleEvaluation(
        rule_id="HSR-005",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.TARGET_LEAKAGE,
        severity=HardSecurityRuleSeverity.CRITICAL,
        outcome=HardSecurityRuleOutcome.TRIGGERED,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        reason_code="TARGET_LEAKAGE",
        evaluation_fingerprint="ef" * 32,
    )

    sec_res = HardSecurityEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        evaluations=[trig_rule],
        triggered_rules=[trig_rule],
        has_triggered_rules=True,
        max_triggered_severity=HardSecurityRuleSeverity.CRITICAL,
        policy_precedence="ALLOW",
        configuration_hash="h" * 64,
        result_fingerprint="rf" * 32,
    )

    is_allow, reasons = engine.evaluate_allow(ctx, calc_res, thresh_res, sec_res)

    assert is_allow is False
    assert "SECURITY_RULE_TRIGGERED_HSR-005" in reasons
