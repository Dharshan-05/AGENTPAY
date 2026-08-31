"""ATIM Durable Workflow Orchestration & State Management Domain Models (Phase 23 / Group 12)."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class WorkflowState(str, Enum):
    """Deterministic workflow instance lifecycle states."""

    INITIATED = "INITIATED"
    STEP_EXECUTING = "STEP_EXECUTING"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowStepType(str, Enum):
    """Supported workflow step types."""

    VALIDATE_INTENT = "VALIDATE_INTENT"
    EVALUATE_SECURITY = "EVALUATE_SECURITY"
    CHECK_LIMITS = "CHECK_LIMITS"
    OBTAIN_HITL = "OBTAIN_HITL"
    EXECUTE_TRANSACTION = "EXECUTE_TRANSACTION"
    RECORD_AUDIT = "RECORD_AUDIT"


class WorkflowStepRecord(BaseModel):
    """Domain model representing an executed workflow step."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: uuid.UUID
    step_index: int
    step_type: WorkflowStepType
    status: str = "COMPLETED"
    payload_hash: str
    input_params: dict[str, Any] = Field(default_factory=dict)
    output_result: Optional[dict[str, Any]] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class WorkflowInstanceRecord(BaseModel):
    """Domain model representing a durable workflow instance."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    workflow_type: str
    state: WorkflowState = WorkflowState.INITIATED
    current_step_index: int = 0
    total_steps: int = 1
    correlation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    signature: Optional[str] = None
