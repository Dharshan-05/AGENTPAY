"""Pydantic Schemas for Payment Failure Handling Subsystem (Phase 296)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.payment import PaymentStatus


class PaymentFailureCategory(StrEnum):
    """Normalized Payment Failure Categories (Phase 296)."""

    AUTHORIZATION_FAILURE = "AUTHORIZATION_FAILURE"
    ORDER_CREATION_FAILURE = "ORDER_CREATION_FAILURE"
    CHECKOUT_FAILURE = "CHECKOUT_FAILURE"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    WEBHOOK_FAILURE = "WEBHOOK_FAILURE"
    TIMEOUT = "TIMEOUT"
    INVALID_REQUEST = "INVALID_REQUEST"
    STATE_TRANSITION_FAILURE = "STATE_TRANSITION_FAILURE"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"


class PaymentFailureCode(StrEnum):
    """Deterministic Payment Failure Reason Codes (Phase 296)."""

    PAYMENT_AUTHORIZATION_DENIED = "PAYMENT_AUTHORIZATION_DENIED"
    PAYMENT_ORDER_CREATION_FAILED = "PAYMENT_ORDER_CREATION_FAILED"
    PAYMENT_PROVIDER_UNAVAILABLE = "PAYMENT_PROVIDER_UNAVAILABLE"
    PAYMENT_VERIFICATION_FAILED = "PAYMENT_VERIFICATION_FAILED"
    PAYMENT_SIGNATURE_INVALID = "PAYMENT_SIGNATURE_INVALID"
    PAYMENT_AMOUNT_MISMATCH = "PAYMENT_AMOUNT_MISMATCH"
    PAYMENT_CURRENCY_MISMATCH = "PAYMENT_CURRENCY_MISMATCH"
    PAYMENT_ORDER_MISMATCH = "PAYMENT_ORDER_MISMATCH"
    PAYMENT_TIMEOUT = "PAYMENT_TIMEOUT"
    PAYMENT_ILLEGAL_STATE_TRANSITION = "PAYMENT_ILLEGAL_STATE_TRANSITION"
    PAYMENT_UNKNOWN_FAILURE = "PAYMENT_UNKNOWN_FAILURE"


class PaymentFailureRecord(BaseModel):
    """Authoritative Normalized Payment Failure Outcome Contract (Phase 296).

    Strictly excludes key_secret, webhook_secret, authorization headers, or raw provider errors.
    Guarantees payment_success=False, payment_verified=False, captured=False.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    failure_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique payment failure record UUID"
    )
    tenant_id: uuid.UUID | None = Field(
        default=None, description="Authoritative tenant UUID context"
    )
    agent_id: uuid.UUID | None = Field(default=None, description="Authoritative agent UUID context")
    transaction_id: str | None = Field(
        default=None, description="Authoritative transaction ID context"
    )
    order_id: str | None = Field(default=None, description="Razorpay order ID if present")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if present")
    event_id: str | None = Field(default=None, description="Provider event ID if present")

    category: PaymentFailureCategory = Field(
        ..., description="Normalized payment failure category enum"
    )
    failure_code: PaymentFailureCode = Field(
        ..., description="Deterministic payment failure code enum"
    )
    safe_message: str = Field(
        ..., description="Sanitized, user-safe failure description (NO secrets or stack traces)"
    )

    previous_status: PaymentStatus | None = Field(
        default=None, description="Payment status prior to failure handling"
    )
    new_status: PaymentStatus = Field(
        default=PaymentStatus.FAILED,
        description="Target payment status (Always FAILED or prior state if transition illegal)",
    )

    payment_success: bool = Field(
        default=False, description="ALWAYS False for payment failure records"
    )
    payment_verified: bool = Field(
        default=False, description="ALWAYS False for payment failure records"
    )
    captured: bool = Field(default=False, description="ALWAYS False for payment failure records")

    failure_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical safe failure metadata"
    )
    failed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Failure handling completion timestamp UTC",
    )
