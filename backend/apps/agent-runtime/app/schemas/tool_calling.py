"""Pydantic Transport Schemas for Tool Calling Framework (Phase 156)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class ToolExecutionState(StrEnum):
    """Deterministic execution state machine for tool calls (Phase 156)."""

    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class ToolContext(BaseModel):
    """Context parameters attached to a tool execution request (Phase 156)."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID | None = Field(default=None, description="Active session UUID")
    task_id: uuid.UUID | None = Field(default=None, description="Active task UUID")
    workflow_id: uuid.UUID | None = Field(default=None, description="Active workflow UUID")
    environment: str = Field(default="production", description="Execution target environment")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Additional context values"
    )  # noqa: E501


class ToolCallRequest(StrictRequestModel):
    """Request contract submitted by agent to execute a registered tool (Phase 156)."""

    tool_id: str = Field(..., min_length=2, max_length=100, description="Target tool ID string")
    tool_version: str | None = Field(
        default=None, max_length=20, description="Optional target version"
    )  # noqa: E501
    arguments: dict[str, Any] = Field(default_factory=dict, description="Tool execution arguments")
    context: ToolContext = Field(default_factory=ToolContext, description="Execution context")
    idempotency_key: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Idempotency key for financial safety",  # noqa: E501
    )
    correlation_id: str | None = Field(
        default=None, max_length=100, description="Correlation tracing ID"
    )  # noqa: E501
    timeout_seconds: float = Field(
        default=30.0, ge=0.5, le=300.0, description="Timeout limit in seconds"
    )  # noqa: E501


class ToolResult(BaseModel):
    """Structured tool execution payload result (Phase 156)."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="success", description="Result status indicator")
    data: dict[str, Any] = Field(default_factory=dict, description="Output payload data")
    logs: list[str] = Field(default_factory=list, description="Execution log entries")


class ToolCallResponse(BaseModel):
    """Response contract returning deterministic tool execution outcome (Phase 156)."""

    model_config = ConfigDict(extra="forbid")

    request_id: uuid.UUID = Field(..., description="Unique tool call execution UUID")
    tool_id: str = Field(..., description="Executed tool ID")
    tool_version: str = Field(..., description="Executed tool version")
    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant UUID")
    state: ToolExecutionState = Field(..., description="Final execution lifecycle state")
    result: ToolResult | None = Field(
        default=None, description="Execution result payload if succeeded"
    )  # noqa: E501
    error: str | None = Field(default=None, description="Structured error message if failed")
    correlation_id: str | None = Field(default=None, description="Correlation tracing ID")
    idempotency_key: str | None = Field(default=None, description="Idempotency key")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")
    executed_at: datetime = Field(..., description="Execution completion timestamp")
