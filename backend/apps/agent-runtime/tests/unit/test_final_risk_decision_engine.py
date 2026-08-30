"""Unit & Mandatory Adversarial Tests for Final Risk Decision Engine (Phases 278-280)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.risk.decisions.decision_engine import FinalRiskDecisionEngine
from app.risk.hard_security_rules import HardSecurityRulesEngine
from app.risk.integrations.fraudguard_risk import FraudGuardRiskIntegrationService
from app.risk.integrations.policy_risk import PolicyRiskIntegrationService
from app.risk.risk_fusion import RiskFusionEngine
from app.risk.risk_score_calculator import RiskScoreCalculator
from app.risk.risk_thresholds import RiskThresholdService
from app.schemas.fraudguard_api import FraudGuardRiskIntelligenceResponse
from app.schemas.ml_risk import PolicyRiskResult
from app.schemas.risk_engine import (
    FinalRiskDecision,
    HardSecurityEvaluationResult,
    HardSecurityRuleEvaluation,
    HardSecurityRuleOutcome,
    HardSecurityRuleSeverity,
    HardSecurityRuleType,
    RiskEvaluationContext,
    RiskScoreCalculationResult,
    RiskScoreUnit,
    RiskSignal,
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


# --- MANDATORY ADVERSARIAL TEST MATRIX ---


def test_adversarial_01_policy_deny_plus_low_risk() -> None:
    """Adversarial Test 1: Policy DENY + Low Risk Score (1.0) -> BLOCK."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=1.0,  # Extremely low advisory risk score!
        composite_risk_score_decimal=Decimal("1.0"),
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
        risk_score=1.0,
        risk_score_decimal=Decimal("1.0"),
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

    res = engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert res.decision == FinalRiskDecision.BLOCK
    assert res.decision_reason == "POLICY_DENY_BLOCK"


def test_adversarial_02_policy_deny_plus_perfect_confidence() -> None:
    """Adversarial Test 2: Policy DENY + Perfect Confidence (1.0) + score 0 -> BLOCK."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=0.0,
        composite_risk_score_decimal=Decimal("0.0"),
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
        policy_precedence="DENY",
        calculation_fingerprint="c" * 64,
    )

    thresh_res = RiskThresholdEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        risk_score=0.0,
        risk_score_decimal=Decimal("0.0"),
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

    res = engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert res.decision == FinalRiskDecision.BLOCK
    assert res.decision_reason == "POLICY_DENY_BLOCK"


def test_adversarial_03_critical_security_plus_low_score() -> None:
    """Adversarial Test 3: Critical Security Triggered + Low Score (2.0) -> BLOCK."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=2.0,
        composite_risk_score_decimal=Decimal("2.0"),
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
        risk_score=2.0,
        risk_score_decimal=Decimal("2.0"),
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

    res = engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert res.decision == FinalRiskDecision.BLOCK
    assert res.decision_reason == "CRITICAL_SECURITY_RULE_BLOCK_HSR-005"


def test_adversarial_04_identity_mismatch_fails_closed() -> None:
    """Adversarial Test 4: Identity Mismatch + Low Score -> Fails closed."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    other_tenant = uuid.uuid4()
    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=other_tenant,  # Cross-tenant attack!
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=2.0,
        composite_risk_score_decimal=Decimal("2.0"),
        score_unit=RiskScoreUnit.RISK_SCORE,
        included_signal_types=[],
        excluded_signal_types=[],
        available_signal_types=[],
        unavailable_signal_types=[],
        applied_weights={},
        total_applied_weight=1.0,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=[],
        policy_precedence="ALLOW",
        calculation_fingerprint="c" * 64,
    )

    thresh_res = RiskThresholdEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        risk_score=2.0,
        risk_score_decimal=Decimal("2.0"),
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

    with pytest.raises(ValueError, match="Tenant ID mismatch across decision components"):
        engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)


def test_adversarial_06_unknown_policy_plus_low_score() -> None:
    """Adversarial Test 6: Unknown Policy + Low Score -> BLOCK."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=2.0,
        composite_risk_score_decimal=Decimal("2.0"),
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
        policy_precedence="UNKNOWN",  # Policy UNKNOWN!
        calculation_fingerprint="c" * 64,
    )

    thresh_res = RiskThresholdEvaluationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        risk_score=2.0,
        risk_score_decimal=Decimal("2.0"),
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
        policy_precedence="UNKNOWN",
        configuration_hash="h" * 64,
        result_fingerprint="rf" * 32,
    )

    res = engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert res.decision == FinalRiskDecision.BLOCK
    assert res.decision_reason == "POLICY_UNKNOWN_BLOCK"


def test_adversarial_09_high_score_plus_policy_allow() -> None:
    """Adversarial Test 9: High Score (85.0) + Policy ALLOW -> BLOCK."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

    calc_res = RiskScoreCalculationResult(
        evaluation_id=ctx.evaluation_id,
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        prediction_timestamp=ctx.prediction_timestamp,
        composite_risk_score=85.0,
        composite_risk_score_decimal=Decimal("85.0"),
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
        risk_score=85.0,
        risk_score_decimal=Decimal("85.0"),
        classification="HIGH",
        matched_threshold_band=RiskThresholdBand.HIGH_RISK_BAND,
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

    res = engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert res.decision == FinalRiskDecision.BLOCK
    assert res.decision_reason == "HIGH_RISK_SCORE_BLOCK"


def test_adversarial_10_medium_score_plus_policy_allow() -> None:
    """Adversarial Test 10: Medium Score (50.0) + Policy ALLOW -> REVIEW."""
    ctx = _make_context()
    engine = FinalRiskDecisionEngine()

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

    res = engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert res.decision == FinalRiskDecision.REVIEW
    assert res.decision_reason == "MEDIUM_RISK_BAND_REVIEW"


def test_end_to_end_pipeline_clean_allow() -> None:
    """End-to-end integration test: Full pipeline evaluation produces ALLOW."""
    ctx = _make_context()

    policy_adapter = PolicyRiskIntegrationService()
    fraud_adapter = FraudGuardRiskIntegrationService()
    fusion_engine = RiskFusionEngine()
    calculator = RiskScoreCalculator()
    thresh_service = RiskThresholdService()
    security_engine = HardSecurityRulesEngine()
    decision_engine = FinalRiskDecisionEngine()

    policy_allow = PolicyRiskResult(
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

    fraud_low = FraudGuardRiskIntelligenceResponse(
        risk_signal_id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        agent_id=ctx.agent_id,
        transaction_id=ctx.transaction_id,
        fraud_probability=0.10,
        transaction_risk_score=10.0,
        risk_level="LOW",
        extracted_factors=[],
        result_fingerprint="r2" * 32,
        evaluated_at=ctx.prediction_timestamp,
    )

    raw_signals: list[RiskSignal] = []
    raw_signals.extend(policy_adapter.integrate_policy_risk(policy_allow, ctx))
    raw_signals.extend(fraud_adapter.integrate_risk_intelligence_response(fraud_low, ctx))

    fused_res = fusion_engine.fuse(ctx, raw_signals)
    calc_res = calculator.calculate_score(fused_res, context=ctx)
    thresh_res = thresh_service.evaluate_thresholds(calc_res, context=ctx)
    sec_res = security_engine.evaluate_rules(ctx, raw_signals, fused_result=fused_res)

    final_res = decision_engine.evaluate_final_decision(ctx, calc_res, thresh_res, sec_res)

    assert final_res.decision == FinalRiskDecision.ALLOW
    assert final_res.decision_reason == "LOW_RISK_ALLOW_CLEAN"
    assert len(final_res.decision_fingerprint) == 64
