"""ATIM Provider Circuit Breaker for managing provider health & failover (Phase 9)."""

from __future__ import annotations

from enum import StrEnum
import logging
import time

from app.core.config import Settings

logger = logging.getLogger("agentpay.atim.routing.circuit_breaker")


class CircuitState(StrEnum):
    """Circuit Breaker States."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class ATIMCircuitBreaker:
    """3-State Circuit Breaker tracking provider failure thresholds and cooldown periods."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.failure_threshold = self.settings.atim_circuit_breaker_threshold
        self.cooldown_seconds = self.settings.atim_circuit_breaker_cooldown

        self._consecutive_failures: dict[str, int] = {}
        self._state: dict[str, CircuitState] = {}
        self._last_failure_time: dict[str, float] = {}

    def get_state(self, provider_name: str) -> CircuitState:
        """Query current circuit breaker state for a provider."""
        current_state = self._state.get(provider_name, CircuitState.CLOSED)
        if current_state == CircuitState.OPEN:
            last_fail = self._last_failure_time.get(provider_name, 0.0)
            if time.time() - last_fail >= self.cooldown_seconds:
                logger.info("Provider '%s' circuit transitioning from OPEN to HALF_OPEN", provider_name)
                self._state[provider_name] = CircuitState.HALF_OPEN
                return CircuitState.HALF_OPEN
        return current_state

    def is_available(self, provider_name: str) -> bool:
        """Check if provider is available to receive requests."""
        state = self.get_state(provider_name)
        return state != CircuitState.OPEN

    def record_success(self, provider_name: str) -> None:
        """Record successful call, resetting failure counts and closing circuit."""
        self._consecutive_failures[provider_name] = 0
        if self._state.get(provider_name) != CircuitState.CLOSED:
            logger.info("Provider '%s' circuit reset to CLOSED", provider_name)
            self._state[provider_name] = CircuitState.CLOSED

    def record_failure(self, provider_name: str) -> None:
        """Record provider failure, tripping circuit to OPEN if threshold exceeded."""
        fails = self._consecutive_failures.get(provider_name, 0) + 1
        self._consecutive_failures[provider_name] = fails
        self._last_failure_time[provider_name] = time.time()

        if fails >= self.failure_threshold:
            logger.warning(
                "Provider '%s' exceeded failure threshold (%d/%d). Circuit tripped to OPEN.",
                provider_name,
                fails,
                self.failure_threshold,
            )
            self._state[provider_name] = CircuitState.OPEN
