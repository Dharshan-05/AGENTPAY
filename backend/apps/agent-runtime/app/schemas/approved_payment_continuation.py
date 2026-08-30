"""Strongly typed schemas for Phase 309 — Approved Payment Continuation Subsystem."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.payment import PaymentStatus, SupportedCurrency


class ApprovedPaymentContinuationCommand(BaseModel):
    """Immutable Command to execute payment continuation post-approval (Phase 309)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_request_id: uuid.UUID = Field(..., description="Target approved request ID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID from session")
    agent_id: uuid.UUID = Field(..., description="Originating agent ID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    amount: Decimal = Field(..., description="Approved payment amount")
    currency: SupportedCurrency = Field(..., description="Approved payment currency")
    idempotency_key: str = Field(..., description="Caller idempotency key")
    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approved request"
    )

    @field_validator("amount")
    @classmethod
    def validate_amount_positive(cls, v: Decimal) -> Decimal:
        if v.is_nan() or v.is_infinite():
            raise ValueError("Amount cannot be NaN or Infinity.")
        if v <= Decimal("0"):
            raise ValueError("Amount must be strictly positive.")
        return v


class ApprovedPaymentContinuationResult(BaseModel):
    """Authoritative result of an approved payment continuation operation (Phase 309)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_request_id: uuid.UUID = Field(..., description="Target approved request ID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID")
    transaction_id: str = Field(..., description="Associated transaction ID")
    agent_id: uuid.UUID = Field(..., description="Associated agent ID")
    amount: Decimal = Field(..., description="Executed monetary amount")
    currency: SupportedCurrency = Field(..., description="Executed currency")
    execution_status: str = Field(
        ..., description="Continuation execution status code (e.g. CONTINUATION_EXECUTED)"
    )
    payment_status: PaymentStatus = Field(
        ..., description="Resulting PaymentStatus managed by PaymentStatusService"
    )
    payment_id: str | None = Field(default=None, description="Provider payment ID if created")
    order_id: str | None = Field(default=None, description="Provider order ID if created")
    execution_fingerprint: str = Field(..., description="SHA-256 execution fingerprint")
    processed_at: datetime = Field(..., description="UTC timestamp of execution")
    is_existing: bool = Field(
        default=False, description="True if result was returned from idempotency cache"
    )
