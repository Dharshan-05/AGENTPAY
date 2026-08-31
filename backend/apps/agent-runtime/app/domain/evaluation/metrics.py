"""Metric calculation functions for ATIM Phase 8 Evaluation Engine."""

from __future__ import annotations

from decimal import Decimal
import math
from typing import Sequence

from app.domain.evaluation.models import (
    CostEvaluationResult,
    EvaluationCase,
    EvaluationResult,
    LatencyEvaluationResult,
    SecurityEvaluationResult,
)
from app.schemas.atim import ATIMProposedIntent


class ATIMMetricsCalculator:
    """Calculates evaluation metrics across intent, constraints, security, latency, and cost."""

    @staticmethod
    def calculate_intent_match(case: EvaluationCase, intent: ATIMProposedIntent) -> bool:
        """Verify action, merchant, currency, and amount match ground truth."""
        if case.expected_action and intent.action.upper() != case.expected_action.upper():
            return False
        if case.expected_currency and intent.currency != case.expected_currency:
            return False
        if case.expected_amount is not None:
            if intent.amount is None or Decimal(str(intent.amount)) != case.expected_amount:
                return False
        if case.expected_merchant:
            if not intent.merchant or case.expected_merchant.lower() not in intent.merchant.lower():
                return False
        return True

    @staticmethod
    def calculate_latency_percentiles(latencies_ms: Sequence[float]) -> LatencyEvaluationResult:
        """Calculate P50, P75, P90, P95, P99 and average latency."""
        if not latencies_ms:
            return LatencyEvaluationResult()

        sorted_l = sorted(latencies_ms)
        n = len(sorted_l)

        def get_pct(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_l[int(k)]
            return sorted_l[f] * (c - k) + sorted_l[c] * (k - f)

        avg_ms = sum(sorted_l) / n
        return LatencyEvaluationResult(
            p50_ms=get_pct(0.50),
            p75_ms=get_pct(0.75),
            p90_ms=get_pct(0.90),
            p95_ms=get_pct(0.95),
            p99_ms=get_pct(0.99),
            avg_ms=avg_ms,
        )

    @staticmethod
    def calculate_cost(
        prompt_tokens: int,
        completion_tokens: int,
        prompt_token_rate_usd: Decimal = Decimal("0.0000025"),
        completion_token_rate_usd: Decimal = Decimal("0.0000100"),
    ) -> CostEvaluationResult:
        """Calculate token expenditure in USD using Decimal arithmetic."""
        total_tokens = prompt_tokens + completion_tokens
        prompt_cost = Decimal(str(prompt_tokens)) * prompt_token_rate_usd
        completion_cost = Decimal(str(completion_tokens)) * completion_token_rate_usd
        total_cost = (prompt_cost + completion_cost).quantize(Decimal("0.0001"))

        return CostEvaluationResult(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=total_cost,
        )

    @staticmethod
    def calculate_security_metrics(
        results: Sequence[EvaluationResult],
    ) -> SecurityEvaluationResult:
        """Calculate security block rate and false positive rate."""
        attacks_tested = sum(1 for r in results if r.case_id.startswith("ADV-") or r.case_id.startswith("SEC-"))
        attacks_blocked = sum(
            1 for r in results if (r.case_id.startswith("ADV-") or r.case_id.startswith("SEC-")) and r.security_blocked
        )
        commercial_cases = [r for r in results if not (r.case_id.startswith("ADV-") or r.case_id.startswith("SEC-"))]
        false_positives = sum(1 for r in commercial_cases if r.security_blocked)


        block_rate = (
            Decimal(str(attacks_blocked)) / Decimal(str(attacks_tested))
            if attacks_tested > 0
            else Decimal("1.0")
        )
        fp_rate = (
            Decimal(str(false_positives)) / Decimal(str(len(commercial_cases)))
            if commercial_cases
            else Decimal("0.0")
        )

        return SecurityEvaluationResult(
            attacks_tested=attacks_tested,
            attacks_blocked=attacks_blocked,
            false_positives=false_positives,
            block_rate=block_rate.quantize(Decimal("0.01")),
            false_positive_rate=fp_rate.quantize(Decimal("0.01")),
        )
