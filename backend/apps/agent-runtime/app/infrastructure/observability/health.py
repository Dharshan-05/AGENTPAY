"""Health and readiness checker module for ATIM (Phase 13 / Group 7)."""

from typing import Any


class ATIMHealthChecker:
    """Component evaluating liveness, readiness, and dependency health."""

    def __init__(self) -> None:
        self._db_healthy = True
        self._redis_healthy = True
        self._llm_provider_healthy = True

    def set_dependency_health(self, dependency: str, is_healthy: bool) -> None:
        """Update health status for a specific dependency."""
        if dependency == "database":
            self._db_healthy = is_healthy
        elif dependency == "redis":
            self._redis_healthy = is_healthy
        elif dependency == "llm":
            self._llm_provider_healthy = is_healthy

    def check_liveness(self) -> dict[str, Any]:
        """Liveness check (proves process is alive)."""
        return {"status": "UP", "component": "agent-runtime"}

    def check_readiness(self) -> dict[str, Any]:
        """Readiness check (proves system can handle financial requests)."""
        is_ready = self._db_healthy and self._llm_provider_healthy
        return {
            "status": "READY" if is_ready else "NOT_READY",
            "dependencies": {
                "database": "UP" if self._db_healthy else "DOWN",
                "redis": "UP" if self._redis_healthy else "DOWN",
                "llm_provider": "UP" if self._llm_provider_healthy else "DOWN",
            },
        }
