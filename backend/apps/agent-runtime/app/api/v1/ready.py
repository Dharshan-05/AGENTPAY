"""API v1 Readiness Check controller for AGENTPAY."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.exceptions.base import ReadinessError
from app.application.services.readiness import ReadinessService
from app.schemas.common import ReadinessResponseData
from app.schemas.errors import ErrorResponse

ready_router = APIRouter(tags=["Readiness"])

_readiness_service_instance = ReadinessService()


def get_readiness_service() -> ReadinessService:
    """Dependency provider for ReadinessService."""
    return _readiness_service_instance


@ready_router.get(
    "/ready",
    operation_id="readiness_check",
    response_model=ReadinessResponseData,
    summary="Readiness Check",
    description=(
        "Determines whether the service is ready to receive normal production "
        "traffic (traffic readiness probe)."
    ),
    responses={
        200: {
            "description": "Service is ready to receive traffic.",
            "model": ReadinessResponseData,
        },
        503: {
            "description": "Service is not ready to receive traffic.",
            "model": ErrorResponse,
        },
    },
)
async def get_readiness(
    readiness_service: Annotated[ReadinessService, Depends(get_readiness_service)],
) -> ReadinessResponseData:
    """API traffic readiness check endpoint.

    Evaluates application and dependency readiness for Kubernetes, Docker,
    and load balancers.
    """
    is_ready = await readiness_service.is_ready()
    if not is_ready:
        raise ReadinessError("Service is not ready.")
    return ReadinessResponseData(status="ready")
