"""Pydantic Transport Schemas for Purchase Request Subsystem (Phase 181)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseRequestCreateRequest(BaseModel):
    """Request contract for converting a purchase plan into a formal purchase request (Phase 181)."""  # noqa: E501

    model_config = ConfigDict(extra="forbid")

    purchase_plan_id: uuid.UUID = Field(..., description="Target Purchase Plan UUID to validate")  # noqa: E501
    idempotency_key: str | None = Field(
        default=None,
        max_length=100,
        description="Optional idempotency key for replay protection",  # noqa: E501
    )


class PurchaseRequestResponse(BaseModel):
    """Response payload for pre-execution purchase request (Phase 181)."""

    model_config = ConfigDict(extra="forbid")

    request_id: uuid.UUID = Field(..., description="Purchase Request UUID (Intent ID)")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    purchase_plan_id: uuid.UUID = Field(..., description="Parent Purchase Plan UUID")
    status: str = Field(
        ...,
        description="Request status (PENDING_APPROVAL, READY_FOR_EXECUTION, REPLAN_REQUIRED)",  # noqa: E501
    )
    requires_approval: bool = Field(
        ..., description="True if human approval workflow is required before execution"
    )
    total_amount: Decimal = Field(..., description="Validated total amount")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    created_at: datetime = Field(..., description="Request creation timestamp")
