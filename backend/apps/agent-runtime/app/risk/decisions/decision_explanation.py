"""Decision Explanation Engine (Phase 282)."""

from __future__ import annotations

import logging

from app.schemas.risk_engine import (
    DecisionExplanationResult,
    FinalRiskDecision,
    FinalRiskDecisionResult,
)

logger = logging.getLogger("agentpay.risk.decisions.explanation")


class DecisionExplanationEngine:
    """Production Decision Explanation Engine (Phase 282).

    Converts authoritative FinalRiskDecisionResult into deterministic explanation
    without recalculating risk, thresholds, or policies.
    """

    def explain_decision(
        self, decision_result: FinalRiskDecisionResult
    ) -> DecisionExplanationResult:
        """Generate deterministic explanation for FinalRiskDecisionResult (Phase 282)."""
        logger.info(
            "Generating explanation for decision %s (tx=%s, decision=%s)",
            decision_result.decision_id,
            decision_result.transaction_id,
            decision_result.decision.value,
        )

        primary_code = decision_result.decision_reason
        contributing_codes: list[str] = []
        contributing_msgs: list[str] = []

        # Map Primary Human-Readable Explanation
        if decision_result.decision == FinalRiskDecision.ALLOW:
            primary_msg = "Transaction risk score is low, policy permits execution, and all hard security rules passed."  # noqa: E501
        elif decision_result.decision == FinalRiskDecision.REVIEW:
            primary_msg = "Transaction requires manual or secondary review before authorization."
        elif decision_result.decision == FinalRiskDecision.BLOCK:
            primary_msg = "Transaction authorization is prohibited due to policy restriction, high risk, or security violation."  # noqa: E501
        else:
            primary_msg = "Transaction evaluation complete."

        # Process Contributing Triggers
        if decision_result.review_reasons:
            contributing_codes.extend(decision_result.review_reasons)
            for r in decision_result.review_reasons:
                contributing_msgs.append(f"Review trigger: {r}")

        if decision_result.block_reasons:
            contributing_codes.extend(decision_result.block_reasons)
            for b in decision_result.block_reasons:
                contributing_msgs.append(f"Block trigger: {b}")

        if decision_result.triggered_rule_ids:
            for rule_id in decision_result.triggered_rule_ids:
                code = f"HARD_SECURITY_RULE_{rule_id}"
                if code not in contributing_codes:
                    contributing_codes.append(code)
                    contributing_msgs.append(f"Hard security rule triggered: {rule_id}")

        if decision_result.cold_start:
            code = "COLD_START_EVIDENCE"
            if code not in contributing_codes:
                contributing_codes.append(code)
                contributing_msgs.append(
                    "Agent has limited historical transaction baseline (cold start)."
                )

        if decision_result.unavailable_signal_types:
            code = (
                f"UNAVAILABLE_SIGNALS_{'_'.join(sorted(decision_result.unavailable_signal_types))}"  # noqa: E501
            )
            if code not in contributing_codes:
                contributing_codes.append(code)
                contributing_msgs.append(
                    f"Required risk signals unavailable: {', '.join(decision_result.unavailable_signal_types)}"  # noqa: E501
                )

        # Deterministic sorting of contributing codes & messages
        sorted_pairs = sorted(
            zip(contributing_codes, contributing_msgs, strict=False), key=lambda x: x[0]
        )
        final_codes = [p[0] for p in sorted_pairs]
        final_msgs = [p[1] for p in sorted_pairs]

        return DecisionExplanationResult(
            evaluation_id=decision_result.evaluation_id,
            decision_id=decision_result.decision_id,
            tenant_id=decision_result.tenant_id,
            agent_id=decision_result.agent_id,
            transaction_id=decision_result.transaction_id,
            prediction_timestamp=decision_result.prediction_timestamp,
            decision=decision_result.decision,
            primary_reason_code=primary_code,
            primary_reason=primary_msg,
            contributing_reason_codes=final_codes,
            contributing_reasons=final_msgs,
            risk_score=decision_result.composite_risk_score,
            threshold_band=decision_result.risk_band,
            policy_precedence=decision_result.policy_precedence,
            security_rule_summary=decision_result.hard_security_status,
            cold_start=decision_result.cold_start,
            unavailable_signal_types=sorted(decision_result.unavailable_signal_types),
            source_fingerprints=sorted(decision_result.source_fingerprints),
            decision_fingerprint=decision_result.decision_fingerprint,
        )
