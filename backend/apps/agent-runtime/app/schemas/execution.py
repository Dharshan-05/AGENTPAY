"""Pydantic Transport Schemas for Agent Execution Loop (Phase 151)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class ExecutionRetryPolicy(BaseModel):
    """Bounded retry policy contract for execution steps (Phase 151)."""

    model_config = ConfigDict(extra="forbid")

    max_attempts: int = Field(
        default=3, ge=1, le=10, description="Maximum execution attempts allowed (1 to 10)"
    )
    backoff_factor: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Exponential backoff factor"
    )


class AgentExecutionCreateRequest(StrictRequestModel):
    """Request payload to initiate controlled agent execution loop (Phase 151).

    Rejects server identity fields (`tenant_id`, `agent_id`, `execution_id`).
    """

    plan_id: uuid.UUID = Field(..., description="Validated purchase plan UUID to execute")
    orchestration_id: uuid.UUID | None = Field(
        default=None, description="Optional associated orchestration decision UUID"
    )
    retry_policy: ExecutionRetryPolicy = Field(
        default_factory=ExecutionRetryPolicy, description="Bounded retry policy configuration"
    )


class ExecutionStepResult(BaseModel):
    """Result status representation for an individual execution loop step (Phase 151)."""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(..., description="Plan step identifier")
    sequence: int = Field(..., description="1-indexed step sequence number")
    action: str = Field(..., description="Step action name")
    status: str = Field(
        ...,
        description="Step status taxonomy",
    )
    started_at: datetime = Field(..., description="Step execution start timestamp")
    completed_at: datetime | None = Field(default=None, description="Step completion timestamp")
    attempt: int = Field(default=1, description="Current execution attempt number")
    duration_ms: float | None = Field(
        default=None, description="Step execution duration in milliseconds"
    )
    error_code: str | None = Field(default=None, description="Safe error code if step failed")
    error_message: str | None = Field(
        default=None, description="Sanitized error message if step failed"
    )
    output_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Sanitized safe output metadata"
    )


class AgentExecutionResponse(BaseModel):
    """Response model returning Agent Execution Loop status representation (Phase 151)."""

    model_config = ConfigDict(extra="forbid")

    execution_id: uuid.UUID = Field(..., description="Unique execution UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    plan_id: uuid.UUID = Field(..., description="Associated purchase plan UUID")
    orchestration_id: uuid.UUID | None = Field(
        default=None, description="Associated orchestration UUID"
    )
    status: str = Field(
        ...,
        description="Execution status taxonomy",
    )
    current_step_sequence: int = Field(
        default=0, description="Current active 1-indexed step sequence"
    )
    total_steps: int = Field(..., description="Total number of plan steps")
    steps: list[ExecutionStepResult] = Field(
        default_factory=list, description="Ordered list of step execution results"
    )
    retry_policy: ExecutionRetryPolicy = Field(..., description="Applied bounded retry policy")
    created_at: datetime = Field(..., description="Execution loop creation timestamp")
    updated_at: datetime = Field(..., description="Execution loop last updated timestamp")
    completed_at: datetime | None = Field(
        default=None, description="Execution loop completion timestamp"
    )
