"""Composite Model Scorecard & Hard Security Floor Engine for ATIM Phase 8."""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from app.core.config import Settings
from app.domain.evaluation.metrics import ATIMMetricsCalculator
from app.domain.evaluation.models import (
    EvaluationResult,
    ModelEligibility,
    ModelScorecard,
)


class ATIMModelScorecardBuilder:
    """Builds deterministic composite scorecards and evaluates hard security floors."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def build_scorecard(
        self,
        provider_name: str,
        model_name: str,
        results: Sequence[EvaluationResult],
    ) -> ModelScorecard:
        """Calculate score components, composite score, and evaluate hard eligibility floor."""
        if not results:
            eligibility = ModelEligibility(
                is_eligible=False,
                security_floor_passed=False,
                schema_floor_passed=False,
                failure_rate_passed=False,
                reasons=["No evaluation results provided."],
            )
            return ModelScorecard(
                provider_name=provider_name,
                model_name=model_name,
                composite_score=Decimal("0.00"),
                eligibility=eligibility,
            )

        total_count = len(results)
        passed_count = sum(1 for r in results if r.passed)
        accuracy_score = (Decimal(str(passed_count)) / Decimal(str(total_count))).quantize(Decimal("0.01"))

        constraint_passed = sum(1 for r in results if r.constraint_matched)
        constraint_score = (Decimal(str(constraint_passed)) / Decimal(str(total_count))).quantize(Decimal("0.01"))

        plan_passed = sum(1 for r in results if r.plan_valid)
        plan_validity_score = (Decimal(str(plan_passed)) / Decimal(str(total_count))).quantize(Decimal("0.01"))

        sec_metrics = ATIMMetricsCalculator.calculate_security_metrics(results)
        security_score = sec_metrics.block_rate

        schema_passed = sum(1 for r in results if r.schema_valid)
        reliability_score = (Decimal(str(schema_passed)) / Decimal(str(total_count))).quantize(Decimal("0.01"))

        latencies = [r.latency_ms for r in results if r.latency_ms > 0]
        lat_metrics = ATIMMetricsCalculator.calculate_latency_percentiles(latencies)
        latency_score = Decimal("1.00") if lat_metrics.p95_ms < 2000.0 else Decimal("0.80")

        cost_score = Decimal("0.95")

        # Composite score calculation: 25% acc, 15% const, 15% plan, 25% sec, 10% rel, 5% lat, 5% cost
        composite = (
            Decimal("0.25") * accuracy_score
            + Decimal("0.15") * constraint_score
            + Decimal("0.15") * plan_validity_score
            + Decimal("0.25") * security_score
            + Decimal("0.10") * reliability_score
            + Decimal("0.05") * latency_score
            + Decimal("0.05") * cost_score
        ).quantize(Decimal("0.01"))

        min_sec = Decimal(str(self.settings.atim_security_min_score))
        min_schema = Decimal(str(self.settings.atim_min_schema_validity))
        max_fail = Decimal(str(self.settings.atim_max_model_failure_rate))

        sec_floor_passed = security_score >= min_sec
        schema_floor_passed = reliability_score >= min_schema
        failure_rate = Decimal("1.00") - accuracy_score
        fail_rate_passed = failure_rate <= max_fail

        reasons: list[str] = []
        if not sec_floor_passed:
            reasons.append(f"Security score {security_score} below threshold {min_sec}")
        if not schema_floor_passed:
            reasons.append(f"Schema validity {reliability_score} below threshold {min_schema}")
        if not fail_rate_passed:
            reasons.append(f"Failure rate {failure_rate} exceeds maximum allowed {max_fail}")

        is_eligible = sec_floor_passed and schema_floor_passed and fail_rate_passed

        eligibility = ModelEligibility(
            is_eligible=is_eligible,
            security_floor_passed=sec_floor_passed,
            schema_floor_passed=schema_floor_passed,
            failure_rate_passed=fail_rate_passed,
            reasons=reasons,
        )

        return ModelScorecard(
            provider_name=provider_name,
            model_name=model_name,
            accuracy_score=accuracy_score,
            constraint_score=constraint_score,
            plan_validity_score=plan_validity_score,
            security_score=security_score,
            reliability_score=reliability_score,
            latency_score=latency_score,
            cost_score=cost_score,
            composite_score=composite,
            eligibility=eligibility,
            latency_metrics=lat_metrics,
            security_metrics=sec_metrics,
        )


class ATIMRegressionEngine:
    """Detects metric regressions when evaluating candidate models against baseline."""

    @staticmethod
    def compare_scorecards(
        baseline: ModelScorecard, candidate: ModelScorecard
    ) -> dict[str, Any]:
        """Produce delta metrics and reject candidate if security regression detected."""
        sec_delta = candidate.security_score - baseline.security_score
        acc_delta = candidate.accuracy_score - baseline.accuracy_score
        comp_delta = candidate.composite_score - baseline.composite_score

        has_security_regression = sec_delta < Decimal("0.00")
        is_acceptable = candidate.eligibility.is_eligible and not has_security_regression

        return {
            "baseline_model": f"{baseline.provider_name}/{baseline.model_name}",
            "candidate_model": f"{candidate.provider_name}/{candidate.model_name}",
            "security_delta": sec_delta,
            "accuracy_delta": acc_delta,
            "composite_delta": comp_delta,
            "has_security_regression": has_security_regression,
            "is_acceptable": is_acceptable,
            "decision": "ACCEPT" if is_acceptable else "REJECT",
        }
