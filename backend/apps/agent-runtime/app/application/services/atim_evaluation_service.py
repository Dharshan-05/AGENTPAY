"""ATIMEvaluationService for managing benchmark runs and scorecards (Phase 8)."""

from __future__ import annotations

import logging
from typing import Sequence

from app.domain.evaluation.models import BenchmarkRun, EvaluationCase, ModelScorecard
from app.domain.evaluation.scoring import ATIMModelScorecardBuilder, ATIMRegressionEngine
from app.infrastructure.evaluation.benchmark_loader import ATIMBenchmarkLoader
from app.infrastructure.evaluation.evaluation_runner import ATIMEvaluationRunner

logger = logging.getLogger("agentpay.atim.evaluation.service")


class ATIMEvaluationService:
    """Application service for running ATIM benchmark suites and generating model scorecards."""

    def __init__(
        self,
        runner: ATIMEvaluationRunner | None = None,
        loader: ATIMBenchmarkLoader | None = None,
        builder: ATIMModelScorecardBuilder | None = None,
    ) -> None:
        self.runner = runner or ATIMEvaluationRunner()
        self.loader = loader or ATIMBenchmarkLoader()
        self.builder = builder or ATIMModelScorecardBuilder()

    async def run_benchmark(
        self,
        dataset_filename: str = "golden_dataset.jsonl",
        provider_name: str = "openai",
        model_name: str = "gpt-4o",
    ) -> BenchmarkRun:
        """Load benchmark dataset, execute evaluation runner, and generate composite scorecard."""
        cases = self.loader.load_dataset(dataset_filename)
        logger.info("Loaded %d evaluation cases from %s", len(cases), dataset_filename)

        results = await self.runner.evaluate_suite(cases, provider_name=provider_name, model_name=model_name)
        scorecard = self.builder.build_scorecard(provider_name, model_name, results)

        return BenchmarkRun(
            dataset_name=dataset_filename,
            scorecards=[scorecard],
        )

    def compare_models(
        self, baseline_scorecard: ModelScorecard, candidate_scorecard: ModelScorecard
    ):
        """Compare candidate model scorecard against baseline for regression detection."""
        return ATIMRegressionEngine.compare_scorecards(baseline_scorecard, candidate_scorecard)
