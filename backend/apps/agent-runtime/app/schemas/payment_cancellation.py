"""Pydantic Schemas for Payment Cancellation Subsystem (Phase 298)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.payment import PaymentStatus


class PaymentCancellationRequest(BaseModel):
    """Authoritative Payment Cancellation Request Contract (Phase 298).

    Binds cancellation request to tenant_id, agent_id, transaction_id, order_id,
    and authorization_fingerprint.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    order_id: str = Field(..., description="Razorpay order ID to be cancelled")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if present")
    authorization_id: uuid.UUID = Field(
        ..., description="Authorization ID granted for payment order"
    )
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint from PaymentAuthorizationResult"
    )
    idempotency_key: str = Field(
        ..., min_length=8, max_length=128, description="Caller idempotency key"
    )
    cancellation_reason: str | None = Field(
        default=None, description="Optional cancellation reason text"
    )


class PaymentCancellationResult(BaseModel):
    """Authoritative Payment Cancellation Result Contract (Phase 298).

    Strictly excludes key_secret, webhook_secret, or credentials.
    Always produces cancellation_status = PaymentStatus.CANCELLED.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    cancellation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique cancellation outcome UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    order_id: str = Field(..., description="Razorpay order ID cancelled")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if present")

    cancellation_status: PaymentStatus = Field(
        default=PaymentStatus.CANCELLED,
        description="Target payment status (Always CANCELLED)",
    )
    previous_status: PaymentStatus = Field(..., description="Payment status prior to cancellation")
    provider_name: str = Field(default="razorpay", description="Payment provider name string")
    cancellation_reason: str | None = Field(
        default=None, description="Optional cancellation reason description"
    )

    cancellation_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical safe cancellation metadata"
    )
    cancelled_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Cancellation completion timestamp UTC",
    )
