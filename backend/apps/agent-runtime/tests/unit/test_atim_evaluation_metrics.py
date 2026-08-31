"""Unit tests for Phase 8 ATIM Metrics Calculator."""

from decimal import Decimal
import pytest

from app.domain.evaluation.metrics import ATIMMetricsCalculator
from app.domain.evaluation.models import EvaluationCase, EvaluationResult
from app.schemas.atim import ATIMProposedIntent


def test_01_intent_match_calculation():
    case = EvaluationCase(
        id="INTENT-101",
        input_text="Buy laptop from Amazon under ₹65,000",
        expected_action="PURCHASE",
        expected_amount=Decimal("65000.00"),
        expected_currency="INR",
        expected_merchant="Amazon",
    )
    matching_intent = ATIMProposedIntent(
        action="PURCHASE",
        amount=Decimal("65000.00"),
        currency="INR",
        merchant="Amazon",
    )
    mismatch_intent = ATIMProposedIntent(
        action="PURCHASE",
        amount=Decimal("70000.00"),
        currency="INR",
        merchant="Amazon",
    )

    assert ATIMMetricsCalculator.calculate_intent_match(case, matching_intent) is True
    assert ATIMMetricsCalculator.calculate_intent_match(case, mismatch_intent) is False


def test_02_latency_percentile_calculation():
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    metrics = ATIMMetricsCalculator.calculate_latency_percentiles(latencies)

    assert metrics.p50_ms == 55.0
    assert metrics.avg_ms == 55.0
    assert metrics.p95_ms > 90.0


def test_03_cost_calculation():
    cost = ATIMMetricsCalculator.calculate_cost(1000, 500)

    assert cost.prompt_tokens == 1000
    assert cost.completion_tokens == 500
    assert cost.total_tokens == 1500
    assert cost.estimated_cost_usd > Decimal("0.0000")


def test_04_security_metrics_calculation():
    results = [
        EvaluationResult(case_id="ADV-001", provider_name="openai", model_name="gpt-4o", passed=True, latency_ms=10.0, security_blocked=True),
        EvaluationResult(case_id="ADV-002", provider_name="openai", model_name="gpt-4o", passed=True, latency_ms=10.0, security_blocked=True),
        EvaluationResult(case_id="COMM-001", provider_name="openai", model_name="gpt-4o", passed=True, latency_ms=10.0, security_blocked=False),
    ]
    sec_metrics = ATIMMetricsCalculator.calculate_security_metrics(results)

    assert sec_metrics.attacks_tested == 2
    assert sec_metrics.attacks_blocked == 2
    assert sec_metrics.block_rate == Decimal("1.00")
    assert sec_metrics.false_positive_rate == Decimal("0.00")
