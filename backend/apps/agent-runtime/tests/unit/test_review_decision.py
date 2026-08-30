"""Unit & Mandatory Security Tests for REVIEW Decision Engine (Phase 279)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.risk.decisions.review_decision import ReviewDecisionEngine
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


def test_01_medium_risk_band_review_qualification() -> None:
    """1. Test MEDIUM_RISK_BAND qualifies for REVIEW."""
    ctx = _make_context()
    engine = ReviewDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=50.0,
        composite_risk_score_decimal=Decimal("50.0"),
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
        risk_score=50.0,
        risk_score_decimal=Decimal("50.0"),
        classification="REVIEW_BAND",
        matched_threshold_band=RiskThresholdBand.MEDIUM_RISK_BAND,
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

    is_review, reasons = engine.evaluate_review(ctx, calc_res, thresh_res, sec_res)

    assert is_review is True
    assert "MEDIUM_RISK_BAND_REVIEW" in reasons


def test_02_policy_deny_prevents_review() -> None:
    """2. Mandatory Security Test: Policy DENY prevents REVIEW (MUST BLOCK instead)."""
    ctx = _make_context()
    engine = ReviewDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=50.0,
        composite_risk_score_decimal=Decimal("50.0"),
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
        risk_score=50.0,
        risk_score_decimal=Decimal("50.0"),
        classification="REVIEW_BAND",
        matched_threshold_band=RiskThresholdBand.MEDIUM_RISK_BAND,
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

    is_review, reasons = engine.evaluate_review(ctx, calc_res, thresh_res, sec_res)

    assert is_review is False
    assert "POLICY_BLOCK_PREVENTED_REVIEW" in reasons


def test_03_critical_security_rule_prevents_review() -> None:
    """3. Mandatory Security Test: Critical hard security rule prevents REVIEW."""
    ctx = _make_context()
    engine = ReviewDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=50.0,
        composite_risk_score_decimal=Decimal("50.0"),
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
        risk_score=50.0,
        risk_score_decimal=Decimal("50.0"),
        classification="REVIEW_BAND",
        matched_threshold_band=RiskThresholdBand.MEDIUM_RISK_BAND,
        configuration_version="1.0.0",
        configuration_hash="t" * 64,
        evaluation_fingerprint="tf" * 32,
    )

    trig_rule = HardSecurityRuleEvaluation(
        rule_id="HSR-003",
        rule_version="1.0.0",
        rule_type=HardSecurityRuleType.IDENTITY_MISMATCH,
        severity=HardSecurityRuleSeverity.CRITICAL,
        outcome=HardSecurityRuleOutcome.TRIGGERED,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        reason_code="IDENTITY_MISMATCH",
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

    is_review, reasons = engine.evaluate_review(ctx, calc_res, thresh_res, sec_res)

    assert is_review is False
    assert "CRITICAL_SECURITY_PREVENTED_REVIEW" in reasons
