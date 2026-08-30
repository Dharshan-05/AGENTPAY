"""Pydantic Schemas for Payment Approval Subsystem (Phase 301)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.payment import SupportedCurrency


class ApprovalStatus(StrEnum):
    """Authoritative Payment Approval Status Enum (Phase 301)."""

    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ApprovalPolicy(BaseModel):
    """Deterministic Approval Policy Configuration (Phase 301)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    policy_version: str = Field(default="1.0.0", description="Approval policy version string")
    high_value_threshold: Decimal = Field(
        default=Decimal("50000.00"), description="Monetary threshold requiring approval"
    )
    auto_approval_risk_cutoff: float = Field(
        default=30.0, description="Risk score cutoff above which approval is required"
    )
    require_approval_for_high_risk: bool = Field(
        default=True, description="Flag requiring approval for high risk scores"
    )


class ApprovalContext(BaseModel):
    """Authoritative Approval Context Contract (Phase 301)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if available")
    order_id: str | None = Field(default=None, description="Razorpay order ID if available")
    authorization_id: uuid.UUID = Field(
        ..., description="Authorization ID granted for payment order"
    )
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint from PaymentAuthorizationResult"
    )
    amount: Decimal = Field(..., description="Monetary amount evaluated for approval")
    currency: SupportedCurrency = Field(..., description="Payment currency enum")
    operation: str = Field(default="payment", description="Requested operation name")
    approval_policy_version: str = Field(
        default="1.0.0", description="Approval policy version applied"
    )


class ApprovalRequest(BaseModel):
    """Authoritative Approval Request Contract (Phase 301).

    CRITICAL INVARIANT: Approval request at creation time CANNOT be self-approved or agent-approved!
    approval_status MUST BE PENDING or NOT_REQUIRED.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique approval request UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    order_id: str | None = Field(default=None, description="Razorpay order ID if available")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if available")

    approval_status: ApprovalStatus = Field(
        ..., description="Current approval status (PENDING or NOT_REQUIRED at creation)"
    )
    risk_score: float = Field(..., description="Composite risk score evaluated")
    amount: Decimal = Field(..., description="Monetary amount evaluated")
    currency: SupportedCurrency = Field(..., description="Payment currency enum")

    approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical approval metadata"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Approval request creation timestamp UTC",
    )

    @field_validator("approval_status")
    @classmethod
    def validate_initial_approval_status(cls, v: ApprovalStatus) -> ApprovalStatus:
        """Enforce Critical Invariant: Agents CANNOT self-approve!

        ApprovalRequest at creation time MUST NOT be APPROVED.
        """
        if v == ApprovalStatus.APPROVED:
            raise ValueError(
                "Critical Security Invariant Violation: Agent requests CANNOT set "
                "approval_status to APPROVED! Must originate from authorized human."
            )
        return v


class ApprovalDecisionRecord(BaseModel):
    """Authoritative Approval Decision Record Contract (Phase 301).

    Records human reviewer decision (APPROVED or REJECTED).
    Forbidden for agent/self-approval.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_id: uuid.UUID = Field(..., description="Target approval request UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    reviewer_id: str = Field(..., description="Authorized human reviewer identifier")

    decision_status: ApprovalStatus = Field(
        ..., description="Reviewer decision outcome (APPROVED or REJECTED)"
    )
    decision_reason: str = Field(..., description="Mandatory decision rationale text")
    decision_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over decision metadata"
    )
    decided_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Review decision completion timestamp UTC",
    )

    @field_validator("reviewer_id")
    @classmethod
    def validate_reviewer_not_agent(cls, v: str) -> str:
        """Enforce Critical Invariant: Reviewer cannot be an automated agent or self-approval."""
        lower_reviewer = v.lower().strip()
        if lower_reviewer in ("agent", "bot", "automated", "self", "system"):
            raise ValueError(
                "Critical Security Invariant Violation: Reviewer ID cannot be an automated agent "
                "or self-approval!"
            )
        return v

    @field_validator("decision_status")
    @classmethod
    def validate_decision_status_enum(cls, v: ApprovalStatus) -> ApprovalStatus:
        """Decision status must be APPROVED or REJECTED."""
        if v not in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            raise ValueError("Decision status must be APPROVED or REJECTED.")
        return v
