"""Application lifespan context manager and service lifecycle state management."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import StrEnum
from typing import Protocol

from fastapi import FastAPI

logger = logging.getLogger("agentpay.lifespan")


class ServiceState(StrEnum):
    """Strongly-typed backend service operational state lifecycle enumeration."""

    STARTING = "starting"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class LifecycleComponent(Protocol):
    """Protocol interface for infrastructure components with lifecycle hooks."""

    @property
    def name(self) -> str:
        """Component identifier name."""
        ...

    async def startup(self) -> None:
        """Component startup hook."""
        ...

    async def shutdown(self) -> None:
        """Component shutdown hook."""
        ...


_current_service_state: ServiceState = ServiceState.STOPPED
_registered_components: list[LifecycleComponent] = []


def get_service_state() -> ServiceState:
    """Return the current global backend service operational state."""
    return _current_service_state


def set_service_state(state: ServiceState) -> None:
    """Update the current global backend service operational state."""
    global _current_service_state
    _current_service_state = state


def register_lifecycle_component(component: LifecycleComponent) -> None:
    """Register an infrastructure component for lifespan startup and shutdown hooks."""
    if not any(c.name == component.name for c in _registered_components):
        _registered_components.append(component)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI application lifespan manager.

    Provides deterministic startup orchestration, status tracking, structured logging,
    and clean teardown hooks for infrastructure components.
    """
    set_service_state(ServiceState.STARTING)
    logger.info(
        "Initializing AGENTPAY application lifecycle...",
        extra={"event": "application.startup"},
    )

    try:
        # Execute startup hooks for registered components
        for component in _registered_components:
            logger.info(
                f"Starting lifecycle component: {component.name}",
                extra={
                    "event": "component.startup",
                    "component": component.name,
                },
            )
            await component.startup()

        set_service_state(ServiceState.READY)
        logger.info(
            "AGENTPAY application lifecycle ready to receive traffic.",
            extra={"event": "application.ready"},
        )
    except Exception as exc:
        set_service_state(ServiceState.FAILED)
        logger.error(
            f"AGENTPAY application startup failed: {exc}",
            extra={"event": "application.startup_failed", "error": str(exc)},
            exc_info=True,
        )
        raise

    try:
        yield
    finally:
        set_service_state(ServiceState.STOPPING)
        logger.info(
            "Shutting down AGENTPAY application lifecycle...",
            extra={"event": "application.shutdown"},
        )

        # Execute shutdown hooks in reverse registration order
        for component in reversed(_registered_components):
            try:
                logger.info(
                    f"Shutting down lifecycle component: {component.name}",
                    extra={
                        "event": "component.shutdown",
                        "component": component.name,
                    },
                )
                await component.shutdown()
            except Exception as exc:
                logger.error(
                    f"Component shutdown error [{component.name}]: {exc}",
                    extra={
                        "event": "application.shutdown_error",
                        "component": component.name,
                        "error": str(exc),
                    },
                    exc_info=True,
                )

        set_service_state(ServiceState.STOPPED)
        logger.info(
            "AGENTPAY application lifecycle shutdown complete.",
            extra={"event": "application.stopped"},
        )
