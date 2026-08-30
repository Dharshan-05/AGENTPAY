"""Pydantic Schemas for Approval Request Engine Subsystem (Phase 302)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.payment import SupportedCurrency


class ApprovalRequestStatus(StrEnum):
    """Authoritative Approval Request Status Enum (Phase 302)."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ApprovalRequestPriority(StrEnum):
    """Approval Request Priority Levels (Phase 302)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ApprovalRequestRecord(BaseModel):
    """Authoritative Immutable Approval Request Record (Phase 302).

    CRITICAL INVARIANT: Upon creation, status MUST be PENDING.
    Cannot be initialized as APPROVED, REJECTED, EXPIRED, or CANCELLED.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique approval request UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    order_id: str | None = Field(default=None, description="Razorpay order ID if available")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if available")

    authorization_id: uuid.UUID = Field(..., description="Payment authorization ID granted by gate")
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 payment authorization fingerprint"
    )
    approval_fingerprint: str = Field(
        ..., description="SHA-256 approval policy evaluation fingerprint"
    )

    amount: Decimal = Field(..., description="Financial payment amount (Decimal)")
    currency: SupportedCurrency = Field(..., description="Payment ISO currency code")
    operation: str = Field(..., description="Requested payment operation name")
    policy_version: str = Field(default="1.0.0", description="Approval policy version applied")

    status: ApprovalRequestStatus = Field(
        default=ApprovalRequestStatus.PENDING,
        description="Current request status (MUST start as PENDING)",
    )
    risk_score: float = Field(..., description="Composite risk score evaluated")
    priority: ApprovalRequestPriority = Field(
        default=ApprovalRequestPriority.MEDIUM, description="Derived approval request priority"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Approval request creation timestamp UTC",
    )
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(hours=24),
        description="Approval request expiration timestamp UTC (Default 24h)",
    )

    @field_validator("status")
    @classmethod
    def validate_initial_status(cls, v: ApprovalRequestStatus) -> ApprovalRequestStatus:
        """Enforce Critical Invariant: Approval request MUST start as PENDING."""
        if v != ApprovalRequestStatus.PENDING:
            raise ValueError(
                f"Critical Invariant Violation: New ApprovalRequestRecord MUST start as PENDING. "
                f"Cannot be initialized as '{v.value}'."
            )
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount_positive(cls, v: Decimal) -> Decimal:
        """Validate positive monetary amount."""
        if v.is_nan() or v.is_infinite():
            raise ValueError("Monetary amount cannot be NaN or Infinity.")
        if v <= Decimal("0"):
            raise ValueError("Monetary amount must be strictly greater than zero.")
        exp = v.as_tuple().exponent
        if isinstance(exp, int) and exp < -2:
            raise ValueError("Monetary amount cannot exceed 2 decimal places.")
        return v


class ApprovalRequestCreateResult(BaseModel):
    """Authoritative Result for Approval Request Creation (Phase 302)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    request_record: ApprovalRequestRecord = Field(
        ..., description="Authoritative approval request record"
    )
    is_existing: bool = Field(
        ..., description="True if replayed existing pending request, False if newly created"
    )
    creation_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint over request creation event"
    )
