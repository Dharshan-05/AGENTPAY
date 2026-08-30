"""Agent Execution Reliability transport schemas for AGENTPAY (Phase 163)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.requests import StrictRequestModel


class RetryClassification(StrEnum):
    """Retry safety classification enum for agent execution (Phase 163)."""

    SAFE_TO_RETRY = "SAFE_TO_RETRY"
    NOT_SAFE_TO_RETRY = "NOT_SAFE_TO_RETRY"
    REQUIRES_RECONCILIATION = "REQUIRES_RECONCILIATION"


class CircuitBreakerState(StrEnum):
    """Circuit breaker state enum (Phase 163)."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class ExecutionRetryRequest(StrictRequestModel):
    """Request schema to attempt safe retry of a failed step or workflow (Phase 163)."""

    workflow_id: uuid.UUID = Field(..., description="Target workflow UUID")
    step_name: str = Field(..., min_length=1, max_length=100, description="Failed step name")
    idempotency_key: str = Field(..., min_length=8, max_length=128, description="Idempotency key")
    force_retry: bool = Field(default=False, description="Explicit force retry override flag")


class ExecutionReconcileRequest(StrictRequestModel):
    """Request schema to reconcile an ambiguous or partial financial execution (Phase 163)."""

    workflow_id: uuid.UUID = Field(..., description="Target workflow UUID")
    payment_order_id: uuid.UUID | None = Field(default=None, description="Payment order UUID")
    resolution_action: str = Field(
        ...,
        pattern="^(CONFIRM_SUCCESS|REVERSE_CHARGE|MARK_FAILED)$",
        description="Resolution strategy",
    )
    reason: str = Field(..., min_length=3, max_length=255, description="Reconciliation reason")


class RetryClassificationResponse(BaseModel):
    """Response schema for retry classification analysis (Phase 163)."""

    classification: RetryClassification
    is_retryable: bool
    is_financial: bool
    reason: str
    suggested_backoff_seconds: float


class CircuitBreakerStatusResponse(BaseModel):
    """Response schema representing circuit breaker status (Phase 163)."""

    service_name: str
    state: CircuitBreakerState
    failure_count: int
    failure_threshold: int
    reset_timeout_seconds: float
    last_failure_at: datetime | None = None


class ExecutionReliabilityResponse(BaseModel):
    """Response schema summarizing execution attempt & recovery state (Phase 163)."""

    execution_id: uuid.UUID
    workflow_id: uuid.UUID
    attempt_count: int
    max_attempts: int
    classification: RetryClassification
    circuit_breaker_state: CircuitBreakerState
    idempotency_key: str
    checkpoint_state: dict[str, Any] = Field(default_factory=dict)
    reconciled: bool = False
    dead_lettered: bool = False
    message: str
