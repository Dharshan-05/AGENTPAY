"""Pydantic Transport & Domain Contracts for Payment Authorization Gate (Phase 285)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

PROHIBITED_PAYMENT_AUTH_KEYS = {
    "final_decision",
    "decision",
    "risk_score",
    "score",
    "override",
    "razorpay_order_id",
    "payment_id",
    "checkout_session",
    "is_fraud",
    "fraud_label",
}


class PaymentAuthorizationOutcome(StrEnum):
    """Authoritative Payment Authorization Gate Outcome Enum (Phase 285)."""

    PERMITTED = "PERMITTED"
    SUSPENDED = "SUSPENDED"
    DENIED = "DENIED"


class PaymentAuthorizationRequest(BaseModel):
    """Input payload for Payment Authorization Gate evaluation (Phase 285)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    payment_reference: str | None = Field(
        default=None, description="Optional payment reference or intent ID binding"
    )
    authorization_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Point-in-time authorization timestamp UTC",
    )
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary context metadata"
    )

    @field_validator("context_metadata")
    @classmethod
    def validate_no_prohibited_overrides_or_leakage(cls, value: dict[str, Any]) -> dict[str, Any]:
        """Reject client-supplied decision forgery, target leakage, or payment execution data."""
        for k in value:
            if k.lower() in PROHIBITED_PAYMENT_AUTH_KEYS:
                raise ValueError(
                    f"Prohibited metadata key '{k}' detected in payment authorization request."
                )
        return value


class PaymentAuthorizationResult(BaseModel):
    """Immutable Outcome Contract produced by Payment Authorization Gate (Phase 285)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    authorization_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique payment authorization run UUID"
    )
    decision_id: uuid.UUID = Field(..., description="Target authoritative decision UUID")
    evaluation_id: uuid.UUID = Field(..., description="Target evaluation run UUID")

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    payment_reference: str | None = Field(
        default=None, description="Bound payment reference / intent ID"
    )

    outcome: PaymentAuthorizationOutcome = Field(
        ..., description="Enforced payment authorization outcome enum"
    )
    execution_permitted: bool = Field(
        ..., description="True ONLY if decision is ALLOW and all security checks pass"
    )
    execution_suspended: bool = Field(
        ..., description="True if decision is REVIEW (requires manual approval)"
    )
    approval_required: bool = Field(
        ..., description="True if human/secondary approval required (REVIEW)"
    )
    authorization_denied: bool = Field(
        ..., description="True if decision is BLOCK or any check failed"
    )

    reason_code: str = Field(..., description="Structured authorization reason code")
    decision_reason: str = Field(..., description="Preserved decision reason code string")
    decision_fingerprint: str = Field(..., description="SHA-256 final decision fingerprint")
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 payment authorization result fingerprint"
    )

    authorized_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Payment authorization timestamp UTC",
    )
