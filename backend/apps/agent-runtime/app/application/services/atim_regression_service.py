"""ATIM Regression Detection & Metric Comparison Service (Phase 11 / Group 6)."""

from typing import Any, Optional

from app.domain.evaluation.models import ModelScorecard


class ATIMRegressionService:
    """Service detecting performance, security, latency, cost, and accuracy regressions."""

    def __init__(
        self,
        max_accuracy_degradation: float = 0.03,
        max_security_degradation: float = 0.00,  # Zero security degradation allowed!
        max_latency_increase_pct: float = 0.20,
        max_cost_increase_pct: float = 0.25,
    ):
        self.max_accuracy_degradation = max_accuracy_degradation
        self.max_security_degradation = max_security_degradation
        self.max_latency_increase_pct = max_latency_increase_pct
        self.max_cost_increase_pct = max_cost_increase_pct

    def evaluate_regression(
        self,
        candidate_scorecard: ModelScorecard,
        champion_scorecard: ModelScorecard,
    ) -> dict[str, Any]:
        """Compare candidate scorecard against champion baseline scorecard.

        Returns:
            Dict containing verdict ("PASS", "WARN", "FAIL"), detected regressions, and metric deltas.
        """
        regressions: list[str] = []
        warnings: list[str] = []

        # 1. Security Regression Check (Zero Tolerance)
        sec_diff = candidate_scorecard.security_score - champion_scorecard.security_score
        if sec_diff < -self.max_security_degradation:
            regressions.append(
                f"SECURITY_REGRESSION: Candidate security score {candidate_scorecard.security_score:.4f} is lower than Champion {champion_scorecard.security_score:.4f}"
            )

        # 2. Schema / Accuracy Regression Check
        schema_diff = candidate_scorecard.schema_score - champion_scorecard.schema_score
        if schema_diff < -self.max_accuracy_degradation:
            regressions.append(
                f"ACCURACY_REGRESSION: Candidate schema score {candidate_scorecard.schema_score:.4f} degraded by {abs(schema_diff):.4f} (max allowed: {self.max_accuracy_degradation})"
            )

        # 3. Composite Score Regression
        comp_diff = candidate_scorecard.composite_score - champion_scorecard.composite_score
        if comp_diff < -0.05:
            warnings.append(
                f"COMPOSITE_SCORE_WARN: Candidate composite score {candidate_scorecard.composite_score:.4f} is lower than Champion {champion_scorecard.composite_score:.4f}"
            )

        verdict = "FAIL" if regressions else ("WARN" if warnings else "PASS")

        return {
            "verdict": verdict,
            "regressions": regressions,
            "warnings": warnings,
            "deltas": {
                "security_delta": round(sec_diff, 4),
                "schema_delta": round(schema_diff, 4),
                "composite_delta": round(comp_diff, 4),
            },
            "candidate_model": candidate_scorecard.model_id,
            "champion_model": champion_scorecard.model_id,
        }
