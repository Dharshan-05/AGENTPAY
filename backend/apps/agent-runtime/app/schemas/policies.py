"""Pydantic Transport Schemas for Policy Management Subsystem (Phases 185–186)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PolicyCreateRequest(BaseModel):
    """Payload contract for creating a Security Policy (Phase 186)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255, description="Policy display name")
    description: str | None = Field(default=None, max_length=500, description="Policy description")
    policy_type: str = Field(
        default="spending",
        description="Policy type (spending, transaction, category, merchant, time, behavior, composite, etc.)",  # noqa: E501
    )
    priority: int = Field(
        default=100, ge=0, description="Priority integer (higher = higher precedence)"
    )  # noqa: E501
    enforcement_mode: str = Field(
        default="enforce", description="Enforcement mode (enforce, monitor, warn, block)"
    )
    starts_at: datetime | None = Field(default=None, description="Optional activation timestamp")
    ends_at: datetime | None = Field(default=None, description="Optional expiration timestamp")
    configuration: dict[str, Any] = Field(
        default_factory=dict, description="Policy configuration payload"
    )


class PolicyUpdateRequest(BaseModel):
    """Payload contract for updating mutable fields of a Security Policy (Phase 186)."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    priority: int | None = Field(default=None, ge=0)
    enforcement_mode: str | None = Field(default=None)
    starts_at: datetime | None = Field(default=None)
    ends_at: datetime | None = Field(default=None)
    configuration: dict[str, Any] | None = Field(default=None)


class PolicyResponse(BaseModel):
    """Safe response model representing a Security Policy (Phases 185–186)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Policy UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    name: str = Field(..., description="Policy name")
    slug: str = Field(..., description="Slug identifier within tenant")
    description: str | None = Field(default=None, description="Policy description")
    status: str = Field(..., description="Lifecycle status (draft, active, inactive, archived)")
    policy_type: str = Field(..., description="Policy classification type")
    priority: int = Field(..., description="Evaluation priority")
    enforcement_mode: str = Field(..., description="Enforcement mode")
    version: int = Field(..., description="Monotonically incrementing version number")
    starts_at: datetime | None = Field(default=None, description="Effective start timestamp")
    ends_at: datetime | None = Field(default=None, description="Effective end timestamp")
    configuration: dict[str, Any] = Field(..., description="Policy configuration rules")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PolicyListResponse(BaseModel):
    """Paginated list response for Security Policies (Phase 186)."""

    model_config = ConfigDict(extra="forbid")

    items: list[PolicyResponse] = Field(..., description="Policy list items")
    total: int = Field(..., ge=0, description="Total matching policy count")
    page: int = Field(..., ge=1, description="Current page index")
    size: int = Field(..., ge=1, description="Page size limit")
