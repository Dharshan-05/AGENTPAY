"""BLOCK Decision Evaluation Engine (Phase 280)."""

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

logger = logging.getLogger("agentpay.risk.decisions.block")


class BlockDecisionEngine:
    """Production BLOCK Decision Evaluation Engine (Phase 280)."""

    def evaluate_block(
        self,
        context: RiskEvaluationContext,
        calc_result: RiskScoreCalculationResult,
        threshold_result: RiskThresholdEvaluationResult,
        security_result: HardSecurityEvaluationResult,
    ) -> tuple[bool, list[str]]:
        """Evaluate whether a transaction qualifies for BLOCK decision (Phase 280)."""
        reasons: list[str] = []
        is_block = False

        pol_prec = calc_result.policy_precedence.upper()

        # 1. Absolute Rule: Policy DENY -> BLOCK
        if pol_prec == "DENY":
            is_block = True
            reasons.append("POLICY_DENY_BLOCK")

        # 2. Absolute Rule: Policy UNKNOWN -> BLOCK
        if pol_prec == "UNKNOWN":
            is_block = True
            reasons.append("POLICY_UNKNOWN_BLOCK")

        # 3. Critical & High Hard Security Rule Triggers
        if security_result.has_triggered_rules:
            for trig in security_result.triggered_rules:
                if trig.severity == HardSecurityRuleSeverity.CRITICAL:
                    is_block = True
                    reasons.append(f"CRITICAL_SECURITY_RULE_BLOCK_{trig.rule_id}")
                elif (
                    trig.severity == HardSecurityRuleSeverity.HIGH
                    and trig.requires_security_intervention
                ):
                    is_block = True
                    reasons.append(f"HIGH_SECURITY_RULE_BLOCK_{trig.rule_id}")

        # 4. High Risk Score Threshold Band -> BLOCK
        if threshold_result.matched_threshold_band == RiskThresholdBand.HIGH_RISK_BAND:
            is_block = True
            reasons.append("HIGH_RISK_SCORE_BLOCK")

        return is_block, reasons
