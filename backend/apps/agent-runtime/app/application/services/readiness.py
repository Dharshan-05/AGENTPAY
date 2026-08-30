"""Application layer readiness service and check abstractions for AGENTPAY."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.lifespan import ServiceState, get_service_state

logger = logging.getLogger("agentpay.application.readiness")


class ReadinessStatus(StrEnum):
    """Strongly-typed readiness status enumeration."""

    READY = "ready"
    NOT_READY = "not_ready"


class ReadinessCheckResult(BaseModel):
    """Diagnostic payload for an individual readiness check."""

    name: str = Field(..., description="Unique check identifier name")
    ready: bool = Field(..., description="Readiness status indicator")
    details: dict[str, Any] | None = Field(
        default=None, description="Optional safe diagnostic metadata"
    )


class ReadinessCheck(ABC):
    """Abstract base class for all readiness checks."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Check identifier name."""
        ...

    @abstractmethod
    async def check(self) -> ReadinessCheckResult:
        """Perform readiness check and return diagnostic result."""
        ...


class ApplicationReadinessCheck(ReadinessCheck):
    """Application-level readiness check verifying lifecycle initialization and configuration."""

    @property
    def name(self) -> str:
        """Check identifier name."""
        return "application"

    async def check(self) -> ReadinessCheckResult:
        """Verify core settings and application operational state."""
        try:
            settings = get_settings()
            service_state = get_service_state()
            is_state_ready = service_state in (ServiceState.READY, ServiceState.STOPPED)
            is_config_ready = bool(settings.environment and settings.app_name)
            is_ready = is_state_ready and is_config_ready
            return ReadinessCheckResult(
                name=self.name,
                ready=is_ready,
                details={
                    "environment": settings.environment.value,
                    "service_state": service_state.value,
                },
            )
        except Exception as exc:
            return ReadinessCheckResult(
                name=self.name,
                ready=False,
                details={"error": str(exc)},
            )


class DatabaseReadinessCheck(ReadinessCheck):
    """Database connectivity readiness check executing lightweight SELECT 1 query."""

    @property
    def name(self) -> str:
        """Check identifier name."""
        return "database"

    async def check(self) -> ReadinessCheckResult:
        """Verify database connectivity via check_database_health."""
        try:
            from app.infrastructure.database.session import check_database_health

            is_healthy = await check_database_health()
            return ReadinessCheckResult(
                name=self.name,
                ready=is_healthy,
                details={"status": "connected" if is_healthy else "unavailable"},
            )
        except Exception:
            return ReadinessCheckResult(
                name=self.name,
                ready=False,
                details={"status": "unavailable", "error": "Database health check error"},
            )


class ReadinessService:
    """Application service for evaluating readiness check registries."""

    def __init__(
        self,
        checks: list[ReadinessCheck] | None = None,
        default_timeout_seconds: float = 2.0,
    ) -> None:
        """Initialize ReadinessService with registered checks."""
        self._checks: list[ReadinessCheck] = (
            checks if checks is not None else [ApplicationReadinessCheck()]
        )
        self._default_timeout_seconds = default_timeout_seconds

    def register_check(self, check: ReadinessCheck) -> None:
        """Register an additional readiness check."""
        self._checks.append(check)

    async def evaluate_readiness(
        self, timeout_seconds: float | None = None
    ) -> tuple[ReadinessStatus, list[ReadinessCheckResult]]:
        """Evaluate all registered checks with bounded execution timeout and fail-closed safety."""
        timeout = timeout_seconds if timeout_seconds is not None else self._default_timeout_seconds
        start_time = time.perf_counter()
        results: list[ReadinessCheckResult] = []
        overall_ready = True

        try:
            async with asyncio.timeout(timeout):
                for check_impl in self._checks:
                    try:
                        res = await check_impl.check()
                        results.append(res)
                        if not res.ready:
                            overall_ready = False
                    except Exception:
                        overall_ready = False
                        results.append(
                            ReadinessCheckResult(
                                name=getattr(check_impl, "name", "unknown"),
                                ready=False,
                                details={"error": "Check execution failed"},
                            )
                        )
        except TimeoutError:
            overall_ready = False
            results.append(
                ReadinessCheckResult(
                    name="timeout",
                    ready=False,
                    details={"error": f"Readiness evaluation timed out after {timeout}s"},
                )
            )
        except Exception:
            overall_ready = False

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        status = ReadinessStatus.READY if overall_ready else ReadinessStatus.NOT_READY

        logger.info(
            "Readiness evaluation completed",
            extra={
                "event": "readiness.check",
                "status": status.value,
                "duration_ms": duration_ms,
                "total_checks": len(results),
            },
        )

        return status, results

    async def is_ready(self, timeout_seconds: float | None = None) -> bool:
        """Return True if all registered readiness checks pass, False otherwise."""
        status, _ = await self.evaluate_readiness(timeout_seconds=timeout_seconds)
        return status == ReadinessStatus.READY
