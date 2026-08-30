"""Standardized error transport data schemas for AGENTPAY."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ResponseMeta


class ErrorDetail(BaseModel):
    """Granular field or contextual error item schema."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    field: str | None = Field(default=None, description="Target field or parameter path")


class ErrorPayload(BaseModel):
    """Standardized inner error structure schema."""

    code: str = Field(..., description="Machine-readable error classification code")
    message: str = Field(..., description="Human-readable summary message")
    details: Any | None = Field(
        default=None, description="Granular error details or validation list"
    )


class ErrorResponse(BaseModel):
    """Canonical top-level API error response envelope schema."""

    success: Literal[False] = Field(default=False, description="Failure status indicator")
    error: ErrorPayload = Field(..., description="Structured error payload")
    meta: ResponseMeta = Field(..., description="Response metadata envelope")
