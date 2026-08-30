"""Unit & Security Tests for Decision Explanation Engine (Phase 282)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.risk.decisions.decision_explanation import DecisionExplanationEngine
from app.schemas.risk_engine import (
    FinalRiskDecision,
    FinalRiskDecisionResult,
    RiskThresholdBand,
)


def test_01_explain_allow_decision() -> None:
    """1. Test explanation generation for ALLOW decision."""
    engine = DecisionExplanationEngine()
    dec_res = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_explain_01",
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.ALLOW,
        decision_reason="LOW_RISK_ALLOW_CLEAN",
        composite_risk_score=12.0,
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="ALLOW",
        hard_security_status="PASSED",
        triggered_rule_ids=[],
        review_reasons=[],
        block_reasons=[],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="df" * 32,
    )

    exp = engine.explain_decision(dec_res)

    assert exp.decision == FinalRiskDecision.ALLOW
    assert exp.primary_reason_code == "LOW_RISK_ALLOW_CLEAN"
    assert "low" in exp.primary_reason.lower()
    assert exp.decision_fingerprint == dec_res.decision_fingerprint


def test_02_explain_block_decision_with_contributing_reasons() -> None:
    """2. Test explanation for BLOCK decision with multiple triggers."""
    engine = DecisionExplanationEngine()
    dec_res = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_explain_02",
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.BLOCK,
        decision_reason="CRITICAL_SECURITY_RULE_BLOCK_HSR-001",
        composite_risk_score=95.0,
        risk_band=RiskThresholdBand.HIGH_RISK_BAND,
        policy_precedence="DENY",
        hard_security_status="TRIGGERED_CRITICAL",
        triggered_rule_ids=["HSR-001"],
        review_reasons=[],
        block_reasons=["POLICY_DENY_BLOCK", "HIGH_RISK_SCORE_BLOCK"],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="df" * 32,
    )

    exp = engine.explain_decision(dec_res)

    assert exp.decision == FinalRiskDecision.BLOCK
    assert "POLICY_DENY_BLOCK" in exp.contributing_reason_codes
    assert "HIGH_RISK_SCORE_BLOCK" in exp.contributing_reason_codes
    assert "HARD_SECURITY_RULE_HSR-001" in exp.contributing_reason_codes


def test_03_explanation_does_not_mutate_decision() -> None:
    """3. Mandatory Security Test: Explanation Engine does not override decision."""  # noqa: E501
    engine = DecisionExplanationEngine()
    dec_res = FinalRiskDecisionResult(
        evaluation_id=uuid.uuid4(),
        decision_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        transaction_id="tx_explain_03",
        prediction_timestamp=datetime.now(UTC),
        decision=FinalRiskDecision.BLOCK,
        decision_reason="POLICY_DENY_BLOCK",
        composite_risk_score=5.0,  # Low score!
        risk_band=RiskThresholdBand.LOW_RISK_BAND,
        policy_precedence="DENY",
        hard_security_status="TRIGGERED_CRITICAL",
        triggered_rule_ids=["HSR-001"],
        review_reasons=[],
        block_reasons=["POLICY_DENY_BLOCK"],
        available_signal_types=["FRAUDGUARD"],
        unavailable_signal_types=[],
        cold_start=False,
        policy_authoritative=True,
        threshold_configuration_version="1.0.0",
        threshold_configuration_hash="t" * 64,
        weight_configuration_version="1.0.0",
        weight_configuration_hash="w" * 64,
        source_fingerprints=["s1"],
        calculation_fingerprint="c" * 64,
        decision_fingerprint="df" * 32,
    )

    exp = engine.explain_decision(dec_res)

    assert exp.decision == FinalRiskDecision.BLOCK  # Preserved! Never converted to ALLOW!
