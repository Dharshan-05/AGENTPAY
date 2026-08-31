"""Failure Injection Abstraction & Chaos Resilience Manager (Phase 14 / Group 7)."""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger("agentpay.atim.failure_injection")

# Test-only environment flag. Defaults to False!
ATIM_FAILURE_INJECTION_ENABLED = (
    os.getenv("ATIM_FAILURE_INJECTION_ENABLED", "false").lower() == "true"
)


class FailureInjector:
    """Test-only failure injection controller for chaos resilience testing."""

    def __init__(self, enabled: bool = ATIM_FAILURE_INJECTION_ENABLED) -> None:
        self.enabled = enabled
        self._fault_rules: dict[tuple[str, str], str] = {}

    def inject_fault(self, dependency: str, operation: str, fault_type: str) -> None:
        """Inject a fault rule (test-only context)."""
        if not self.enabled:
            logger.warning("Failure injection requested but disabled in environment configuration.")
            return
        self._fault_rules[(dependency, operation)] = fault_type
        logger.info("Injected fault rule: (%s, %s) -> %s", dependency, operation, fault_type)

    def clear_faults(self) -> None:
        """Clear all injected fault rules."""
        self._fault_rules.clear()

    def should_fail(self, dependency: str, operation: str) -> Optional[str]:
        """Check if a dependency call should fail due to an active injected fault rule.

        Returns:
            Fault type string (e.g. "TIMEOUT", "HTTP_500", "CONNECTION_DROP") or None if healthy.
        """
        if not self.enabled:
            return None
        return self._fault_rules.get((dependency, operation))
