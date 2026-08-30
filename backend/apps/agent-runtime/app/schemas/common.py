"""Common transport data schemas and response envelopes for AGENTPAY."""

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthStatus(BaseModel):
    """Health status transport schema."""

    service: str = Field(..., description="Service identifier")
    status: str = Field(..., description="Operational status indicator")


class HealthCheckData(BaseModel):
    """Process liveness health check response data schema."""

    status: Literal["healthy"] = Field(
        default="healthy", description="Process liveness status indicator"
    )


class ReadinessResponseData(BaseModel):
    """API traffic readiness check response data schema."""

    status: Literal["ready"] = Field(
        default="ready", description="Traffic readiness status indicator"
    )


class ResponseMeta(BaseModel):
    """Standard API response metadata schema."""

    request_id: str = Field(..., description="Unique correlation request ID")
    timestamp: str | None = Field(default=None, description="ISO-8601 UTC timestamp")


class SuccessResponse(BaseModel, Generic[T]):
    """Canonical successful API response envelope schema."""

    success: Literal[True] = Field(default=True, description="Success status indicator")
    data: T = Field(..., description="Response payload data")
    meta: ResponseMeta = Field(..., description="Response metadata envelope")


# Legacy alias for backward compatibility
ResponseMetadata = ResponseMeta
DataResponse = SuccessResponse
