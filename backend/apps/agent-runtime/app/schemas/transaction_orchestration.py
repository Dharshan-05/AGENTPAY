"""Transaction Orchestration transport schemas for AGENTPAY (Phase 161)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.requests import StrictRequestModel


class WorkflowStatus(StrEnum):
    """Workflow state lifecycle enum for transaction orchestration (Phase 161)."""

    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    AUTHORIZED = "AUTHORIZED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    EXECUTING = "EXECUTING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"


class StepExecutionMode(StrEnum):
    """Workflow step execution mode enum (Phase 161)."""

    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    CONDITIONAL = "CONDITIONAL"


class WorkflowStepCreate(StrictRequestModel):
    """Schema for defining an individual workflow step in a transaction (Phase 161)."""

    step_number: int = Field(..., ge=1, description="Sequential step index")
    step_name: str = Field(..., min_length=1, max_length=100, description="Unique step name")
    tool_name: str = Field(..., min_length=1, max_length=100, description="Target tool name")
    execution_mode: StepExecutionMode = Field(
        default=StepExecutionMode.SEQUENTIAL,
        description="Execution mode (SEQUENTIAL, PARALLEL, CONDITIONAL)",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Step arguments/parameters"
    )
    depends_on_steps: list[str] = Field(
        default_factory=list, description="Step names that must complete before this step"
    )
    condition_expr: str | None = Field(
        default=None, description="Optional condition expression for CONDITIONAL mode"
    )


class WorkflowCreateRequest(StrictRequestModel):
    """Request schema for creating a multi-step agent transaction workflow (Phase 161)."""

    session_id: uuid.UUID | None = Field(default=None, description="Optional session UUID")
    task_id: uuid.UUID | None = Field(default=None, description="Optional task UUID")
    workflow_name: str = Field(
        ..., min_length=1, max_length=150, description="Workflow descriptive name"
    )
    steps: list[WorkflowStepCreate] = Field(
        ..., min_length=1, max_length=20, description="Ordered list of workflow steps"
    )
    idempotency_key: str = Field(..., min_length=8, max_length=128, description="Idempotency key")
    amount: float | None = Field(
        default=None, ge=0.0, description="Total financial transaction amount"
    )
    currency: str | None = Field(
        default=None, min_length=3, max_length=3, description="ISO currency code"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional workflow metadata"
    )


class WorkflowCancelRequest(StrictRequestModel):
    """Request schema for cancelling an active workflow (Phase 161)."""

    reason: str = Field(
        ..., min_length=3, max_length=255, description="Reason for workflow cancellation"
    )


class WorkflowStepResponse(BaseModel):
    """Response schema for a single workflow step execution status (Phase 161)."""

    step_number: int
    step_name: str
    tool_name: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
    executed_at: datetime | None = None


class WorkflowResponse(BaseModel):
    """Response schema for agent transaction workflow state (Phase 161)."""

    workflow_id: uuid.UUID
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    session_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    workflow_name: str
    status: WorkflowStatus
    current_step: int
    total_steps: int
    idempotency_key: str
    amount: float | None = None
    currency: str | None = None
    requires_approval: bool = False
    approval_id: uuid.UUID | None = None
    steps: list[WorkflowStepResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
