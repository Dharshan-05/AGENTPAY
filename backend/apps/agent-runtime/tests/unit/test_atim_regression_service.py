"""Unit tests for ATIM Regression Service (Phase 11 / Group 6)."""

from datetime import datetime

import pytest

from app.application.services.atim_regression_service import ATIMRegressionService
from app.domain.evaluation.models import ModelEligibility, ModelScorecard


@pytest.fixture
def regression_service():
    return ATIMRegressionService()


def test_01_evaluate_regression_pass(regression_service):
    champ = ModelScorecard(
        model_id="openai/gpt-4o",
        composite_score=0.98,
        accuracy_score=0.97,
        security_score=0.99,
        schema_score=0.98,
        latency_score=0.95,
        cost_score=0.90,
        eligibility=ModelEligibility.ELIGIBLE,
        created_at=datetime.utcnow(),
    )
    cand = ModelScorecard(
        model_id="anthropic/claude-3-5-sonnet-20241022",
        composite_score=0.98,
        accuracy_score=0.97,
        security_score=0.99,
        schema_score=0.98,
        latency_score=0.95,
        cost_score=0.90,
        eligibility=ModelEligibility.ELIGIBLE,
        created_at=datetime.utcnow(),
    )

    res = regression_service.evaluate_regression(cand, champ)
    assert res["verdict"] == "PASS"
    assert len(res["regressions"]) == 0


def test_02_evaluate_regression_security_fail(regression_service):
    champ = ModelScorecard(
        model_id="openai/gpt-4o",
        composite_score=0.98,
        accuracy_score=0.97,
        security_score=0.99,
        schema_score=0.98,
        latency_score=0.95,
        cost_score=0.90,
        eligibility=ModelEligibility.ELIGIBLE,
        created_at=datetime.utcnow(),
    )
    cand = ModelScorecard(
        model_id="unsafe_model",
        composite_score=0.80,
        accuracy_score=0.97,
        security_score=0.94,  # Security degraded!
        schema_score=0.98,
        latency_score=0.95,
        cost_score=0.90,
        eligibility=ModelEligibility.INELIGIBLE_SECURITY_FLOOR,
        created_at=datetime.utcnow(),
    )

    res = regression_service.evaluate_regression(cand, champ)
    assert res["verdict"] == "FAIL"
    assert any("SECURITY_REGRESSION" in r for r in res["regressions"])
