"""Unit tests for Phase 9 Circuit Breaker."""

import pytest

from app.application.services.atim_circuit_breaker import ATIMCircuitBreaker, CircuitState


def test_01_circuit_breaker_trips_to_open_after_failures():
    cb = ATIMCircuitBreaker()
    provider = "test_provider"

    assert cb.get_state(provider) == CircuitState.CLOSED
    assert cb.is_available(provider) is True

    # Record 3 failures (threshold = 3)
    cb.record_failure(provider)
    cb.record_failure(provider)
    cb.record_failure(provider)

    assert cb.get_state(provider) == CircuitState.OPEN
    assert cb.is_available(provider) is False


def test_02_circuit_breaker_resets_on_success():
    cb = ATIMCircuitBreaker()
    provider = "test_provider"

    cb.record_failure(provider)
    cb.record_failure(provider)
    cb.record_success(provider)

    assert cb.get_state(provider) == CircuitState.CLOSED
    assert cb.is_available(provider) is True
