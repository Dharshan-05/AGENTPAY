"""API v1 Process Liveness Health Check controller for AGENTPAY."""

from fastapi import APIRouter

from app.schemas.common import HealthCheckData

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    operation_id="health_check",
    response_model=HealthCheckData,
    summary="Health Check",
    description=(
        "Determines whether the application process is alive and capable of "
        "serving HTTP requests (process liveness probe)."
    ),
)
async def get_health() -> HealthCheckData:
    """Process liveness health check endpoint.

    Lightweight, asynchronous, dependency-free check for Kubernetes,
    Docker, CI/CD pipelines, and load balancers.
    """
    return HealthCheckData(status="healthy")
