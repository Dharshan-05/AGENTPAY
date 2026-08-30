"""REVIEW Decision Evaluation Engine (Phase 279)."""

from __future__ import annotations

import logging

from app.schemas.risk_engine import (
    HardSecurityEvaluationResult,
    HardSecurityRuleSeverity,
    RiskEvaluationContext,
    RiskScoreCalculationResult,
    RiskThresholdBand,
    RiskThresholdEvaluationResult,
)

logger = logging.getLogger("agentpay.risk.decisions.review")


class ReviewDecisionEngine:
    """Production REVIEW Decision Evaluation Engine (Phase 279)."""

    def evaluate_review(
        self,
        context: RiskEvaluationContext,
        calc_result: RiskScoreCalculationResult,
        threshold_result: RiskThresholdEvaluationResult,
        security_result: HardSecurityEvaluationResult,
    ) -> tuple[bool, list[str]]:
        """Evaluate whether a transaction qualifies for REVIEW decision (Phase 279)."""
        reasons: list[str] = []
        is_review = False

        pol_prec = calc_result.policy_precedence.upper()

        # BLOCK conditions prevent REVIEW from overriding BLOCK
        if pol_prec in ("DENY", "UNKNOWN"):
            return False, ["POLICY_BLOCK_PREVENTED_REVIEW"]

        for trig in security_result.triggered_rules:
            if trig.severity == HardSecurityRuleSeverity.CRITICAL:
                return False, ["CRITICAL_SECURITY_PREVENTED_REVIEW"]

        if threshold_result.matched_threshold_band == RiskThresholdBand.HIGH_RISK_BAND:
            return False, ["HIGH_RISK_BAND_PREVENTED_REVIEW"]

        # REVIEW Triggers
        if threshold_result.matched_threshold_band == RiskThresholdBand.MEDIUM_RISK_BAND:
            is_review = True
            reasons.append("MEDIUM_RISK_BAND_REVIEW")

        if pol_prec in ("REQUIRE_APPROVAL", "REVIEW"):
            is_review = True
            reasons.append("POLICY_REVIEW_REQUIRED")

        if calc_result.unavailable_signal_types:
            is_review = True
            reasons.append("MANDATORY_SIGNAL_UNAVAILABLE_REVIEW")

        for trig in security_result.triggered_rules:
            if trig.severity in (
                HardSecurityRuleSeverity.HIGH,
                HardSecurityRuleSeverity.MEDIUM,
                HardSecurityRuleSeverity.LOW,
            ):
                is_review = True
                reasons.append(f"SECURITY_RULE_REVIEW_{trig.rule_id}")

        return is_review, reasons
