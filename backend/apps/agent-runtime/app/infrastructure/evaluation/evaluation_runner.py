"""Evaluation runner executing benchmark suites against LLM router and ATIM components."""

from __future__ import annotations

import time
from typing import Sequence

from app.application.services.atim_security.security_classifier import ATIMSecurityClassifier
from app.application.services.llm_intent_extractor_provider import LLMIntentExtractorProvider
from app.domain.evaluation.metrics import ATIMMetricsCalculator
from app.domain.evaluation.models import EvaluationCase, EvaluationResult
from app.domain.evaluation.scoring import ATIMModelScorecardBuilder


class ATIMEvaluationRunner:
    """Executes evaluation cases and produces evaluation results."""

    def __init__(
        self,
        intent_extractor: LLMIntentExtractorProvider | None = None,
        security_classifier: ATIMSecurityClassifier | None = None,
    ) -> None:
        self.intent_extractor = intent_extractor or LLMIntentExtractorProvider()
        self.security_classifier = security_classifier or ATIMSecurityClassifier()

    async def evaluate_case(
        self, case: EvaluationCase, provider_name: str = "openai", model_name: str = "gpt-4o"
    ) -> EvaluationResult:
        """Run single evaluation case through ATIM Security Classifier & LLM Extractor."""
        start_t = time.perf_counter()

        # 1. Security Check
        sec_decision = self.security_classifier.evaluate_security(case.input_text)
        if case.is_adversarial:
            latency_ms = (time.perf_counter() - start_t) * 1000.0
            return EvaluationResult(
                case_id=case.id,
                provider_name=provider_name,
                model_name=model_name,
                passed=not sec_decision.allowed,
                latency_ms=latency_ms,
                security_blocked=not sec_decision.allowed,
                plan_valid=True,
                schema_valid=True,
            )

        if not sec_decision.allowed:
            latency_ms = (time.perf_counter() - start_t) * 1000.0
            return EvaluationResult(
                case_id=case.id,
                provider_name=provider_name,
                model_name=model_name,
                passed=False,
                latency_ms=latency_ms,
                security_blocked=True,
                error_message="Security classifier blocked non-adversarial prompt",
            )

        # 2. Intent Extraction Check
        try:
            intent = await self.intent_extractor.extract(case.input_text, {})
            latency_ms = (time.perf_counter() - start_t) * 1000.0
            intent_matched = ATIMMetricsCalculator.calculate_intent_match(case, intent)
            ambiguity_matched = intent.is_ambiguous == case.expected_is_ambiguous

            passed = intent_matched and ambiguity_matched
            return EvaluationResult(
                case_id=case.id,
                provider_name=provider_name,
                model_name=model_name,
                passed=passed,
                latency_ms=latency_ms,
                intent_matched=intent_matched,
                ambiguity_matched=ambiguity_matched,
                schema_valid=True,
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - start_t) * 1000.0
            return EvaluationResult(
                case_id=case.id,
                provider_name=provider_name,
                model_name=model_name,
                passed=False,
                latency_ms=latency_ms,
                schema_valid=False,
                error_message=str(exc),
            )

    async def evaluate_suite(
        self,
        cases: Sequence[EvaluationCase],
        provider_name: str = "openai",
        model_name: str = "gpt-4o",
    ) -> list[EvaluationResult]:
        """Execute sequence of evaluation cases."""
        results: list[EvaluationResult] = []
        for case in cases:
            res = await self.evaluate_case(case, provider_name=provider_name, model_name=model_name)
            results.append(res)
        return results
