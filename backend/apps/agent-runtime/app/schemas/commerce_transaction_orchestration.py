"""Pydantic Transport Schemas for Commerce Transaction Orchestration Subsystem (Phase 184)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CommerceExecutionRequest(BaseModel):
    """Request contract for executing a commerce purchase request (Phase 184)."""

    model_config = ConfigDict(extra="forbid")

    purchase_request_id: uuid.UUID = Field(..., description="Target Purchase Request UUID")
    idempotency_key: str | None = Field(
        default=None,
        max_length=100,
        description="Optional idempotency key for replay protection",  # noqa: E501
    )


class CommerceExecutionResponse(BaseModel):
    """Response payload for commerce transaction execution orchestration (Phase 184)."""

    model_config = ConfigDict(extra="forbid")

    execution_id: uuid.UUID = Field(..., description="Orchestration Execution UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    purchase_request_id: uuid.UUID = Field(..., description="Target Purchase Request UUID")
    status: str = Field(
        ...,
        description="Execution status (VALIDATING, AUTHORIZED, PENDING_APPROVAL, READY_FOR_EXECUTION, EXECUTING, COMPLETED, FAILED, REQUIRES_RECONCILIATION, CANCELLED)",  # noqa: E501
    )
    requires_approval: bool = Field(
        ..., description="True if human approval workflow is currently required"
    )
    approval_id: uuid.UUID | None = Field(
        default=None, description="Human approval request UUID, if created"
    )
    total_amount: Decimal = Field(..., description="Total executed amount")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    executed_at: datetime = Field(..., description="Execution status timestamp")
