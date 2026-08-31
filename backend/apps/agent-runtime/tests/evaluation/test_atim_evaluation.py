"""Evaluation benchmark test suite for ATIM Phase 8."""

import pytest

from app.application.services.atim_evaluation_service import ATIMEvaluationService


@pytest.mark.asyncio
async def test_01_golden_dataset_benchmark_run():
    service = ATIMEvaluationService()

    run_result = await service.run_benchmark(
        dataset_filename="golden_dataset.jsonl",
        provider_name="openai",
        model_name="gpt-4o",
    )

    assert run_result.dataset_name == "golden_dataset.jsonl"
    assert len(run_result.scorecards) == 1

    scorecard = run_result.scorecards[0]
    assert scorecard.provider_name == "openai"
    assert scorecard.model_name == "gpt-4o"
    assert scorecard.composite_score >= 0.0
    assert scorecard.eligibility.security_floor_passed is True
