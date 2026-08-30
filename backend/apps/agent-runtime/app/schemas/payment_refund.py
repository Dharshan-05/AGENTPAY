"""Pydantic Schemas for Payment Refund Subsystem (Phase 299)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.payment import PaymentStatus, SupportedCurrency


class PaymentRefundRequest(BaseModel):
    """Authoritative Payment Refund Request Contract (Phase 299).

    Supports full and partial refunds with strict monetary Decimal validation.
    Binds refund request to tenant_id, agent_id, transaction_id, order_id, payment_id.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    order_id: str = Field(..., description="Razorpay order ID for payment")
    payment_id: str = Field(..., description="Razorpay payment ID to be refunded")
    captured_amount: Decimal = Field(..., gt=0, description="Original captured monetary amount")
    refund_amount: Decimal = Field(
        ..., gt=0, description="Monetary amount to refund (>0, <= captured_amount)"
    )
    currency: SupportedCurrency = Field(..., description="Payment currency enum")
    authorization_id: uuid.UUID = Field(
        ..., description="Authorization ID granted for payment order"
    )
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint from PaymentAuthorizationResult"
    )
    idempotency_key: str = Field(
        ..., min_length=8, max_length=128, description="Caller idempotency key"
    )
    refund_reason: str | None = Field(default=None, description="Optional refund reason text")

    @field_validator("captured_amount", "refund_amount")
    @classmethod
    def validate_monetary_decimal(cls, v: Decimal) -> Decimal:
        """Validate decimal monetary precision (maximum 2 decimal places, no NaN/Infinity)."""
        if v.is_nan() or v.is_infinite():
            raise ValueError("Monetary amount cannot be NaN or Infinity.")
        if v <= Decimal("0"):
            raise ValueError("Monetary amount must be strictly greater than zero.")
        exp = v.as_tuple().exponent
        if isinstance(exp, int) and exp < -2:
            raise ValueError("Monetary amount cannot exceed 2 decimal places.")
        return v


class PaymentRefundResult(BaseModel):
    """Authoritative Payment Refund Result Contract (Phase 299).

    Strictly excludes key_secret, webhook_secret, or credentials.
    Always produces refund_status = PaymentStatus.REFUNDED.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    refund_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique refund outcome UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    order_id: str = Field(..., description="Razorpay order ID")
    payment_id: str = Field(..., description="Razorpay payment ID refunded")
    provider_refund_id: str = Field(..., description="Provider-generated refund ID (rfnd_...)")

    refund_amount: Decimal = Field(..., description="Monetary amount refunded")
    captured_amount: Decimal = Field(..., description="Original captured monetary amount")
    currency: SupportedCurrency = Field(..., description="Payment currency enum")

    refund_status: PaymentStatus = Field(
        default=PaymentStatus.REFUNDED,
        description="Target payment status (Always REFUNDED)",
    )
    previous_status: PaymentStatus = Field(
        default=PaymentStatus.CAPTURED,
        description="Payment status prior to refund (Always CAPTURED)",
    )
    provider_name: str = Field(default="razorpay", description="Payment provider name string")
    refund_reason: str | None = Field(default=None, description="Optional refund reason text")

    refund_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical safe refund metadata"
    )
    refunded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Refund completion timestamp UTC",
    )
