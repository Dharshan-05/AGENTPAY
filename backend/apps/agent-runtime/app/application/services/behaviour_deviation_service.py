"""Behaviour Deviation Application Service for AGENTPAY (Phase 202)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.behaviour_deviation import (
    BehaviourDeviationRequest,
    BehaviourDeviationResult,
)

logger = logging.getLogger("agentguard.security.behaviour_deviation")


class BehaviourDeviationService:
    """Production Behaviour Deviation Engine (Phase 202 - Advisory Subsystem Only)."""

    def evaluate_deviation(
        self,
        request: BehaviourDeviationRequest,
    ) -> BehaviourDeviationResult:
        """Evaluate proposed action against historical behaviour baseline (Phase 202)."""
        now = datetime.now(UTC)
        baseline = request.baseline

        # 1. Cold start / Insufficient history check
        if not baseline.baseline_available:
            return BehaviourDeviationResult(
                has_deviation=False,
                severity="COLD_START",
                deviation_score=Decimal("0.00"),
                reason_codes=["INSUFFICIENT_HISTORY"],
                explanation="Insufficient historical observations to establish a behavioural baseline.",  # noqa: E501
                evaluated_at=now,
            )

        reason_codes: list[str] = []
        highest_severity = "NORMAL"
        score_accumulator = Decimal("0.00")

        # 2. Amount Deviation Check (Decimal precision)
        if request.amount is not None and baseline.amount_stats:
            stats = baseline.amount_stats
            if request.amount > stats.max_amount * Decimal("2.00"):
                reason_codes.append("AMOUNT_DEVIATION_CRITICAL")
                highest_severity = "CRITICAL"
                score_accumulator += Decimal("0.50")
            elif request.amount > stats.average_amount * Decimal("2.50"):
                reason_codes.append("AMOUNT_DEVIATION_HIGH")
                if highest_severity not in ("CRITICAL",):
                    highest_severity = "HIGH"
                score_accumulator += Decimal("0.35")

        # 3. Merchant Deviation Check
        if request.merchant_id and baseline.frequent_merchants:
            m_str = str(request.merchant_id).lower()
            if m_str not in baseline.frequent_merchants:
                reason_codes.append("UNFAMILIAR_MERCHANT_DEVIATION")
                if highest_severity not in ("CRITICAL", "HIGH"):
                    highest_severity = "MEDIUM"
                score_accumulator += Decimal("0.25")

        # 4. Category Deviation Check
        if request.category and baseline.frequent_categories:
            c_str = request.category.strip().lower()
            if c_str not in baseline.frequent_categories:
                reason_codes.append("UNFAMILIAR_CATEGORY_DEVIATION")
                if highest_severity not in ("CRITICAL", "HIGH", "MEDIUM"):
                    highest_severity = "LOW"
                score_accumulator += Decimal("0.15")

        # 5. Currency Deviation Check
        if request.currency and baseline.frequent_currencies:
            curr_str = request.currency.strip().upper()
            if curr_str not in baseline.frequent_currencies:
                reason_codes.append("UNFAMILIAR_CURRENCY_DEVIATION")
                if highest_severity not in ("CRITICAL", "HIGH"):
                    highest_severity = "MEDIUM"
                score_accumulator += Decimal("0.25")

        has_deviation = len(reason_codes) > 0
        final_score = min(score_accumulator, Decimal("1.00"))

        if has_deviation:
            explanation = f"Behaviour deviation detected: {', '.join(reason_codes)} (Severity: {highest_severity})."  # noqa: E501
        else:
            explanation = "Proposed action aligns with historical behavioural baseline."

        return BehaviourDeviationResult(
            has_deviation=has_deviation,
            severity=highest_severity,
            deviation_score=final_score,
            reason_codes=reason_codes,
            explanation=explanation,
            evaluated_at=now,
        )
