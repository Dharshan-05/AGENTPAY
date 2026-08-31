"""Unit tests for Phase 9 Intelligent Router."""

from decimal import Decimal
import uuid
import pytest

from app.application.services.atim_circuit_breaker import ATIMCircuitBreaker
from app.application.services.atim_intelligent_router import (
    ATIMIntelligentRouter,
    RequestComplexity,
    RiskLevel,
    RoutingTaskType,
)
from app.application.services.atim_model_registry import ATIMModelRegistry, ModelProfile


def test_01_request_classification():
    router = ATIMIntelligentRouter()

    task, complexity, risk = router.classify_request("What is my balance?", {})
    assert risk == RiskLevel.LOW
    assert task == RoutingTaskType.GENERAL_AGENT_INTELLIGENCE

    task, complexity, risk = router.classify_request("Buy a laptop from Amazon for ₹65,000", {})
    assert risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert task == RoutingTaskType.INTENT_EXTRACTION


def test_02_route_request_selects_eligible_model():
    router = ATIMIntelligentRouter()

    decision = router.route_request("Buy a laptop from Amazon for ₹65,000")

    assert decision.selected_provider in ("openai", "anthropic")
    assert decision.security_floor_enforced is True
    assert decision.eligible_models_count > 0


def test_03_route_request_falls_back_when_circuits_open():
    cb = ATIMCircuitBreaker()
    cb.record_failure("openai")
    cb.record_failure("openai")
    cb.record_failure("openai")

    cb.record_failure("anthropic")
    cb.record_failure("anthropic")
    cb.record_failure("anthropic")

    router = ATIMIntelligentRouter(circuit_breaker=cb)
    decision = router.route_request("Buy a laptop")

    assert decision.fallback_route == "rule_engine_fallback"
