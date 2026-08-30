"""ALLOW Decision Evaluation Engine (Phase 278)."""

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

logger = logging.getLogger("agentpay.risk.decisions.allow")


class AllowDecisionEngine:
    """Production ALLOW Decision Evaluation Engine (Phase 278)."""

    def evaluate_allow(
        self,
        context: RiskEvaluationContext,
        calc_result: RiskScoreCalculationResult,
        threshold_result: RiskThresholdEvaluationResult,
        security_result: HardSecurityEvaluationResult,
    ) -> tuple[bool, list[str]]:
        """Evaluate whether a transaction meets all mandatory ALLOW invariants (Phase 278)."""
        reasons: list[str] = []
        is_allow = True

        # 1. Identity & Context Integrity Check
        if (
            calc_result.tenant_id != context.tenant_id
            or threshold_result.tenant_id != context.tenant_id
            or security_result.tenant_id != context.tenant_id
        ):
            is_allow = False
            reasons.append("IDENTITY_TENANT_MISMATCH")

        if (
            calc_result.agent_id != context.agent_id
            or threshold_result.agent_id != context.agent_id
            or security_result.agent_id != context.agent_id
        ):
            is_allow = False
            reasons.append("IDENTITY_AGENT_MISMATCH")

        if (
            calc_result.transaction_id != context.transaction_id
            or threshold_result.transaction_id != context.transaction_id
            or security_result.transaction_id != context.transaction_id
        ):
            is_allow = False
            reasons.append("IDENTITY_TRANSACTION_MISMATCH")

        # 2. Policy Authority Invariant
        pol_prec = calc_result.policy_precedence.upper()
        if pol_prec == "DENY":
            is_allow = False
            reasons.append("POLICY_DENY_RESTRICTION")
        elif pol_prec == "UNKNOWN":
            is_allow = False
            reasons.append("POLICY_UNKNOWN_RESTRICTION")
        elif pol_prec in ("REQUIRE_APPROVAL", "REVIEW"):
            is_allow = False
            reasons.append("POLICY_REVIEW_REQUIRED")

        # 3. Hard Security Rules Invariant
        if security_result.has_triggered_rules:
            for trig in security_result.triggered_rules:
                if trig.severity in (
                    HardSecurityRuleSeverity.CRITICAL,
                    HardSecurityRuleSeverity.HIGH,
                ):
                    is_allow = False
                    reasons.append(f"SECURITY_RULE_TRIGGERED_{trig.rule_id}")

        # 4. Risk Threshold Band Invariant
        if threshold_result.matched_threshold_band != RiskThresholdBand.LOW_RISK_BAND:
            is_allow = False
            reasons.append(f"RISK_BAND_NOT_LOW_{threshold_result.matched_threshold_band.value}")

        # 5. Cold Start & Signal Availability Invariant
        if any("cold_start" in s for s in calc_result.excluded_signal_types):
            is_allow = False
            reasons.append("COLD_START_AMBIGUITY")

        if calc_result.unavailable_signal_types:
            is_allow = False
            reasons.append(
                f"MANDATORY_SIGNAL_UNAVAILABLE_{'_'.join(calc_result.unavailable_signal_types)}"
            )

        if is_allow:
            reasons.append("LOW_RISK_ALLOW_CLEAN")

        return is_allow, reasons
