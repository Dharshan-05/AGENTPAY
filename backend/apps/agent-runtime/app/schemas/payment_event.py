"""Pydantic Schemas for Payment Event Processing (Phase 295)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.payment import PaymentStatus, SupportedCurrency


class NormalizedPaymentEventType(StrEnum):
    """Normalized Domain Payment Event Types (Phase 295)."""

    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    PAYMENT_CAPTURED = "PAYMENT_CAPTURED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_REFUNDED = "PAYMENT_REFUNDED"
    REFUND_FAILED = "REFUND_FAILED"
    DISPUTE_CREATED = "DISPUTE_CREATED"
    UNKNOWN_EVENT = "UNKNOWN_EVENT"


class PaymentEventProcessingStatus(StrEnum):
    """Status outcomes for Payment Event Processing (Phase 295)."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    MISMATCH = "MISMATCH"
    IGNORED = "IGNORED"
    ILLEGAL_TRANSITION = "ILLEGAL_TRANSITION"
    ALREADY_PROCESSED = "ALREADY_PROCESSED"
    ERROR = "ERROR"


class PaymentEventProcessingResult(BaseModel):
    """Authoritative Normalized Payment Event Processing Outcome Contract (Phase 295).

    Strictly excludes key_secret or webhook_secret.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    processing_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique processing execution UUID"
    )
    envelope_id: uuid.UUID = Field(..., description="Source VerifiedWebhookEnvelope UUID")
    provider: str = Field(default="razorpay", description="Payment provider name")
    event_id: str | None = Field(default=None, description="Provider event ID if present")
    raw_event_type: str = Field(..., description="Original provider event type string")
    normalized_event_type: NormalizedPaymentEventType = Field(
        ..., description="Normalized domain event type enum"
    )

    tenant_id: uuid.UUID | None = Field(
        default=None, description="Authoritative tenant UUID context"
    )
    agent_id: uuid.UUID | None = Field(default=None, description="Authoritative agent UUID context")
    transaction_id: str | None = Field(
        default=None, description="Authoritative transaction ID context"
    )
    order_id: str | None = Field(default=None, description="Razorpay order ID")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID")

    previous_status: PaymentStatus | None = Field(
        default=None, description="Source payment status before event processing"
    )
    new_status: PaymentStatus | None = Field(
        default=None, description="Target payment status after event processing"
    )
    processing_status: PaymentEventProcessingStatus = Field(
        ..., description="Authoritative event processing status enum"
    )
    reason_code: str = Field(..., description="Structured processing outcome rationale")

    currency: SupportedCurrency | None = Field(
        default=None, description="Verified event currency if available"
    )

    processing_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical result fields"
    )
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event processing completion timestamp UTC",
    )
