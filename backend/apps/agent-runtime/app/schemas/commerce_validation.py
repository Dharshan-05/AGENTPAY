"""Pydantic Transport Schemas for Commerce Validation Subsystem (Phase 182)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CommerceValidationError(BaseModel):
    """Single validation error entry for commerce request (Phase 182)."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Deterministic error code (e.g. STALE_PLAN, PRICE_CHANGED)")
    message: str = Field(..., description="Human-readable error explanation")
    field: str | None = Field(default=None, description="Optional target field or entity name")


class CommerceValidationResult(BaseModel):
    """Authoritative validation result payload for commerce transaction context (Phase 182)."""  # noqa: E501

    model_config = ConfigDict(extra="forbid")

    valid: bool = Field(
        ..., description="True if complete commerce request is valid and executable"
    )  # noqa: E501
    purchase_request_id: uuid.UUID = Field(..., description="Purchase Request UUID")
    purchase_plan_id: uuid.UUID = Field(..., description="Parent Purchase Plan UUID")
    currency: str = Field(..., description="Unified ISO currency code")
    subtotal: Decimal = Field(..., description="Gross subtotal amount")
    discount_total: Decimal = Field(..., description="Total discount savings")
    total: Decimal = Field(..., description="Net total payable amount")
    requires_approval: bool = Field(..., description="True if human approval policy is triggered")
    validation_errors: list[CommerceValidationError] = Field(
        default_factory=list, description="Validation errors preventing execution"
    )
    warnings: list[str] = Field(default_factory=list, description="Advisory warnings or notes")
    validated_at: datetime = Field(..., description="Validation execution timestamp")
