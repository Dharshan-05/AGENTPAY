"""Pydantic Schemas for Secure Agent-to-Razorpay Boundary Subsystem (Phase 300)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.payment import SupportedCurrency


class AgentPaymentOperation(StrEnum):
    """Allowed Agent Payment Operations Allowlist (Phase 300)."""

    CREATE_ORDER = "create_order"
    CHECKOUT = "checkout"
    VERIFY = "verify"
    CANCEL = "cancel"
    REFUND = "refund"


class AgentPaymentCommand(BaseModel):
    """Authoritative Agent Payment Command Contract (Phase 300).

    Agent acts as a requester ONLY, never a payment authority.
    Forbids direct credentials, secrets, raw status, capture state, or approval manipulation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    operation: AgentPaymentOperation = Field(
        ..., description="Requested payment operation from allowlist"
    )

    authorization_id: uuid.UUID = Field(
        ..., description="Authorization ID granted by PaymentAuthorizationGate"
    )
    authorization_fingerprint: str = Field(..., description="SHA-256 authorization fingerprint")
    idempotency_key: str = Field(
        ..., min_length=8, max_length=128, description="Caller idempotency key"
    )

    # Operation payload fields (Optional depending on operation)
    amount: Decimal | None = Field(default=None, description="Monetary amount if applicable")
    currency: SupportedCurrency | None = Field(
        default=None, description="Currency enum if applicable"
    )
    order_id: str | None = Field(default=None, description="Razorpay order ID if applicable")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if applicable")
    signature: str | None = Field(
        default=None, description="Payment verification signature if applicable"
    )
    captured_amount: Decimal | None = Field(
        default=None, description="Captured amount if refund operation"
    )
    refund_amount: Decimal | None = Field(
        default=None, description="Refund amount if refund operation"
    )
    reason: str | None = Field(default=None, description="Optional cancellation/refund reason")

    @field_validator("amount", "captured_amount", "refund_amount")
    @classmethod
    def validate_decimal_amounts(cls, v: Decimal | None) -> Decimal | None:
        """Validate decimal monetary precision if provided."""
        if v is None:
            return None
        if v.is_nan() or v.is_infinite():
            raise ValueError("Monetary amount cannot be NaN or Infinity.")
        if v <= Decimal("0"):
            raise ValueError("Monetary amount must be strictly greater than zero.")
        exp = v.as_tuple().exponent
        if isinstance(exp, int) and exp < -2:
            raise ValueError("Monetary amount cannot exceed 2 decimal places.")
        return v


class AgentPaymentResponse(BaseModel):
    """Authoritative Agent Payment Response Contract (Phase 300).

    Strictly excludes key_secret, webhook_secret, or credentials.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    command_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique command execution outcome UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    operation: AgentPaymentOperation = Field(..., description="Executed operation")

    status: str = Field(..., description="Execution status description")
    command_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over safe command result payload"
    )
    result_payload: dict[str, Any] = Field(
        ..., description="Safe result dictionary containing outcome metadata"
    )
    executed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Command execution completion timestamp UTC",
    )
