"""Pydantic Transport Schemas for Tool Execution Audit Subsystem (Phase 159)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolAuditResponse(BaseModel):
    """Response contract returning an immutable tool execution audit record (Phase 159)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Audit primary key UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    user_id: uuid.UUID | None = Field(default=None, description="Requesting User UUID")
    execution_id: uuid.UUID = Field(..., description="Tool execution session UUID")
    request_id: str | None = Field(default=None, description="Request ID string")
    correlation_id: str | None = Field(default=None, description="Correlation tracing ID")
    tool_id: str = Field(..., description="Executed tool ID")
    tool_version: str = Field(..., description="Executed tool version")
    permission_decision: str = Field(
        ..., description="Authorization decision (ALLOW, DENY, REQUIRE_APPROVAL)"
    )  # noqa: E501
    approval_state: str = Field(
        ..., description="Approval state (APPROVED, PENDING, REJECTED, NOT_REQUIRED)"
    )  # noqa: E501
    execution_state: str = Field(..., description="Final execution lifecycle state")
    risk_classification: str = Field(..., description="Risk level classification")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")
    error_code: str | None = Field(default=None, description="Error code if failed")
    environment: str = Field(..., description="Execution environment")
    payload_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Sanitized payload metadata"
    )  # noqa: E501
    created_at: datetime = Field(..., description="Audit event creation timestamp")


class ToolAuditListResponse(BaseModel):
    """Paginated list response contract for tool execution audit records (Phase 159)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_count: int = Field(..., description="Count of audit records in current page")
    has_more: bool = Field(..., description="True if next page exists")
    audits: list[ToolAuditResponse] = Field(default_factory=list, description="Audit records")
