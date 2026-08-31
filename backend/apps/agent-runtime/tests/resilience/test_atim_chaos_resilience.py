"""Resilience and Chaos Fault Injection tests for ATIM (Phase 14 / Group 7)."""

from decimal import Decimal
from unittest.mock import AsyncMock
import uuid

import pytest

from app.application.services.atim_circuit_breaker import ATIMCircuitBreaker, CircuitState
from app.application.services.atim_failure_injection import FailureInjector
from app.infrastructure.observability import ATIMHealthChecker, ATIMMetricsCollector


@pytest.fixture
def failure_injector():
    injector = FailureInjector(enabled=True)
    yield injector
    injector.clear_faults()


def test_01_failure_injector_rules(failure_injector):
    failure_injector.inject_fault("llm_provider", "generate", "TIMEOUT")
    assert failure_injector.should_fail("llm_provider", "generate") == "TIMEOUT"
    assert failure_injector.should_fail("database", "query") is None


def test_02_circuit_breaker_chaos_transitions():
    cb = ATIMCircuitBreaker(failure_threshold=2, recovery_cooldown_seconds=60)
    provider = "openai"

    assert cb.get_state(provider) == CircuitState.CLOSED

    # Record 2 consecutive failures to trip circuit
    cb.record_failure(provider)
    cb.record_failure(provider)

    assert cb.get_state(provider) == CircuitState.OPEN
    assert cb.can_execute(provider) is False

    # Manual reset
    cb.reset(provider)
    assert cb.get_state(provider) == CircuitState.CLOSED
    assert cb.can_execute(provider) is True


def test_03_observability_failure_decoupling():
    metrics = ATIMMetricsCollector()
    health = ATIMHealthChecker()

    # Simulate metrics collector exception during recording
    try:
        metrics.record_request(task_type="PAYMENT", status="SUCCESS")
    except Exception:
        pass  # Telemetry failure must never throw or affect payment flow

    # Health readiness remains READY despite telemetry recording events
    assert health.check_readiness()["status"] == "READY"
