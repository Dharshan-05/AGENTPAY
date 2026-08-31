"""Unit tests for Phase 8 Regression Engine."""

from decimal import Decimal
import pytest

from app.domain.evaluation.models import EvaluationResult
from app.domain.evaluation.scoring import ATIMModelScorecardBuilder, ATIMRegressionEngine


def test_01_regression_detection_rejects_candidate_with_lower_security():
    builder = ATIMModelScorecardBuilder()

    baseline_results = [
        EvaluationResult(case_id="INT-001", provider_name="openai", model_name="gpt-4o", passed=True, latency_ms=100.0),
        EvaluationResult(case_id="ADV-001", provider_name="openai", model_name="gpt-4o", passed=True, latency_ms=100.0, security_blocked=True),
    ]
    baseline_card = builder.build_scorecard("openai", "gpt-4o", baseline_results)

    candidate_results = [
        EvaluationResult(case_id="INT-001", provider_name="cand", model_name="cand-model", passed=True, latency_ms=50.0),
        EvaluationResult(case_id="ADV-001", provider_name="cand", model_name="cand-model", passed=False, latency_ms=50.0, security_blocked=False),
    ]
    candidate_card = builder.build_scorecard("cand", "cand-model", candidate_results)

    comparison = ATIMRegressionEngine.compare_scorecards(baseline_card, candidate_card)

    assert comparison["has_security_regression"] is True
    assert comparison["decision"] == "REJECT"
