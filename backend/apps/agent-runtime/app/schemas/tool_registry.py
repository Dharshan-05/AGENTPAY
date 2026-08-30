"""Pydantic Transport Schemas for Tool Registry Subsystem (Phase 157)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class ToolStatus(StrEnum):
    """Lifecycle states for registered agent tools (Phase 157)."""

    REGISTERED = "REGISTERED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    DEPRECATED = "DEPRECATED"
    REMOVED = "REMOVED"


class ToolRiskClassification(StrEnum):
    """Risk classifications for registered agent tools (Phase 157)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ToolRegisterRequest(StrictRequestModel):
    """Request contract for registering a new tool in the Tool Registry (Phase 157)."""

    tool_id: str = Field(..., min_length=2, max_length=100, description="Unique string ID for tool")
    name: str = Field(..., min_length=2, max_length=150, description="Descriptive tool name")
    version: str = Field(
        default="1.0.0", min_length=1, max_length=20, description="Semantic version string"
    )  # noqa: E501
    description: str = Field(
        ..., min_length=5, max_length=500, description="Detailed tool description"
    )  # noqa: E501
    category: str = Field(
        default="utility", min_length=2, max_length=50, description="Functional category"
    )  # noqa: E501
    owner: str | None = Field(
        default=None, max_length=150, description="Tool owner/maintainer email"
    )  # noqa: E501
    environment: str = Field(default="production", max_length=50, description="Target environment")
    risk_classification: ToolRiskClassification = Field(
        default=ToolRiskClassification.LOW, description="Risk classification level"
    )
    input_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for input parameter validation"
    )
    output_schema: dict[str, Any] | None = Field(
        default=None, description="Optional JSON Schema for output response validation"
    )
    capabilities: list[str] = Field(
        default_factory=list, description="Capability tags provided by this tool"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional registry metadata"
    )


class ToolUpdateRequest(StrictRequestModel):
    """Request contract for updating a tool definition in the Tool Registry (Phase 157)."""

    description: str | None = Field(default=None, min_length=5, max_length=500)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    owner: str | None = Field(default=None, max_length=150)
    status: ToolStatus | None = Field(default=None)
    environment: str | None = Field(default=None, max_length=50)
    risk_classification: ToolRiskClassification | None = Field(default=None)
    input_schema: dict[str, Any] | None = Field(default=None)
    output_schema: dict[str, Any] | None = Field(default=None)
    capabilities: list[str] | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(default=None)


class ToolResponse(BaseModel):
    """Response contract returning structured representation of a tool definition (Phase 157)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Internal UUIDv7 primary key")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    tool_id: str = Field(..., description="Tool unique identifier string")
    name: str = Field(..., description="Tool name")
    version: str = Field(..., description="Tool version string")
    description: str = Field(..., description="Tool description")
    category: str = Field(..., description="Tool functional category")
    owner: str | None = Field(default=None, description="Tool owner/maintainer")
    status: ToolStatus = Field(..., description="Current tool status")
    environment: str = Field(..., description="Deployment environment")
    risk_classification: ToolRiskClassification = Field(
        ..., description="Risk level classification"
    )  # noqa: E501
    input_schema: dict[str, Any] = Field(..., description="Input validation JSON Schema")
    output_schema: dict[str, Any] | None = Field(
        default=None, description="Output validation JSON Schema"
    )  # noqa: E501
    capabilities: list[str] = Field(default_factory=list, description="Provided capabilities")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Tool metadata")
    created_at: datetime = Field(..., description="Registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ToolListResponse(BaseModel):
    """Response model returning a list of registered tool definitions (Phase 157)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_count: int = Field(..., description="Count of tools returned")
    tools: list[ToolResponse] = Field(default_factory=list, description="Tool definition records")
