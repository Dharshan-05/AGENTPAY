"""Pydantic Schemas for Human Approval Subsystem (Phases 162 & 310)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.approval_workflow import ApprovalDecisionType
from app.schemas.payment import SupportedCurrency
from app.schemas.reviewer_authorization import (
    ReviewerPermission,
    ReviewerRole,
)
from app.schemas.risk_engine import RiskThresholdBand

# =====================================================================
# PHASE 162 SCHEMAS (Preserved for Backward Compatibility)
# =====================================================================


class ApprovalRiskLevel(StrEnum):
    """Approval Risk Level Enum (Phase 162)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ApprovalStatus(StrEnum):
    """Approval Request Status Enum (Phase 162)."""

    PENDING_APPROVAL = "PENDING_APPROVAL"
    AUTO_APPROVED = "AUTO_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalPolicyEvaluationResponse(BaseModel):
    """Approval Policy Evaluation Response (Phase 162)."""

    model_config = ConfigDict(extra="forbid")

    requires_approval: bool
    risk_level: ApprovalRiskLevel
    required_approvals_count: int
    matched_policy_name: str
    auto_approved: bool


class ApprovalRequestCreate(BaseModel):
    """Approval Request Creation Schema (Phase 162)."""

    model_config = ConfigDict(extra="ignore")

    action_name: str = "payment"
    amount: float = 0.0
    currency: str = "USD"
    context_data: dict[str, Any] = {}
    reason: str | None = None
    session_id: str | uuid.UUID | None = None
    task_id: str | uuid.UUID | None = None
    workflow_id: str | uuid.UUID | None = None


class ApprovalRequestResponse(BaseModel):
    """Approval Request Response Schema (Phase 162)."""

    model_config = ConfigDict(extra="ignore")

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    action_name: str = "payment"
    amount: float = 0.0
    currency: str = "USD"
    status: str = "PENDING"
    required_approvals: int = 1
    received_approvals: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    approval_id: uuid.UUID | None = None
    requesting_user_id: uuid.UUID | None = None
    risk_level: ApprovalRiskLevel | None = None
    required_approvals_count: int | None = None
    current_approvals_count: int | None = None
    reason: str | None = None
    updated_at: datetime | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.approval_id is None:
            object.__setattr__(self, "approval_id", self.id)


class ApprovalDecisionRequest(BaseModel):
    """Approval Decision Request Schema (Phase 162)."""

    model_config = ConfigDict(extra="ignore")

    decision: str
    reason: str | None = None


class ApprovalDecisionResponse(BaseModel):
    """Approval Decision Response Schema (Phase 162)."""

    model_config = ConfigDict(extra="ignore")

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    approval_request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    reviewer_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    decision: str = "APPROVE"
    reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    decision_id: uuid.UUID | None = None
    approval_id: uuid.UUID | None = None
    reviewer_email: str | None = None
    decided_at: datetime | None = None


# =====================================================================
# PHASE 310 SCHEMAS (Production Human Approval Integration)
# =====================================================================

FORBIDDEN_AUTOMATED_IDENTITIES: set[str] = {
    "agent",
    "bot",
    "automated",
    "automation",
    "system",
    "self",
    "ai",
    "ai_agent",
    "service",
    "scheduler",
}


class HumanReviewerIdentityError(ValueError):
    """Exception raised when an identity fails human verification."""


class HumanReviewerContext(BaseModel):
    """Trusted Authenticated Human Reviewer Context (Phase 310).

    MUST originate from trusted server-side authentication (e.g. session / auth context).
    Enforces human identity verification and forbids automated/agent identities.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    reviewer_id: uuid.UUID = Field(..., description="Authoritative human reviewer UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    reviewer_email: str | None = Field(default=None, description="Authenticated reviewer email")
    reviewer_role: ReviewerRole = Field(
        default=ReviewerRole.REVIEWER, description="Assigned reviewer role"
    )
    permissions: set[ReviewerPermission] = Field(
        default_factory=set, description="Set of assigned explicit permissions"
    )
    session_id: str | None = Field(default=None, description="Authenticated session correlation ID")
    authenticated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Session authentication timestamp UTC",
    )
    authorization_limit: Decimal = Field(
        default=Decimal("50000.00"), description="Configured maximum monetary approval limit"
    )
    is_human_verified: bool = Field(
        default=True, description="Explicit verification that identity belongs to a human"
    )

    @field_validator("is_human_verified")
    @classmethod
    def validate_human_verification(cls, v: bool) -> bool:
        """Enforce that human verification boolean is True."""
        if not v:
            raise ValueError("Reviewer identity MUST be human-verified.")
        return v

    @field_validator("authorization_limit")
    @classmethod
    def validate_limit_positive(cls, v: Decimal) -> Decimal:
        """Validate non-negative approval limit."""
        if v.is_nan() or v.is_infinite():
            raise ValueError("Authorization limit cannot be NaN or Infinity.")
        if v < Decimal("0"):
            raise ValueError("Authorization limit cannot be negative.")
        return v


def verify_human_identity_string(identity_str: str) -> None:
    """Validate that an identity string does not contain forbidden automated keywords."""
    clean_str = identity_str.strip().lower()
    if clean_str in FORBIDDEN_AUTOMATED_IDENTITIES:
        raise HumanReviewerIdentityError(
            f"Identity '{identity_str}' is recognized as an automated identity. "
            "Human approval requires an authenticated human reviewer."
        )


class HumanReviewContextResponse(BaseModel):
    """Safe UX Contract exposing request context for human review decision (Phase 310).

    EXCLUDES all sensitive credentials, provider secrets, or auth tokens.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(..., description="Target approval request UUID")
    tenant_id: uuid.UUID = Field(..., description="Target tenant UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    agent_id: uuid.UUID = Field(..., description="Originating AI agent UUID")
    amount: Decimal = Field(..., description="Monetary amount requested")
    currency: SupportedCurrency = Field(..., description="Currency requested")
    risk_score: float = Field(..., description="Point-in-time composite risk score [0, 100]")
    risk_band: RiskThresholdBand = Field(..., description="Risk threshold band")
    priority: str = Field(..., description="Approval priority (CRITICAL, HIGH, MEDIUM, LOW)")
    status: ApprovalRequestStatus = Field(..., description="Current request status")
    approval_fingerprint: str = Field(..., description="Canonical SHA-256 fingerprint")
    created_at: datetime = Field(..., description="Request creation timestamp UTC")
    expires_at: datetime = Field(..., description="Request expiration timestamp UTC")


class HumanApprovalCommand(BaseModel):
    """Command payload to execute human approval for a payment request (Phase 310)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(..., description="Target approval request UUID")
    tenant_id: uuid.UUID = Field(..., description="Target tenant UUID context")
    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approved request"
    )
    reviewer_comment: str | None = Field(
        default=None, description="Optional human reviewer comment (Max 500 chars)"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")
    auto_continue: bool = Field(
        default=True, description="True to trigger Phase 309 approved payment continuation"
    )

    @field_validator("reviewer_comment")
    @classmethod
    def validate_comment_length(cls, v: str | None) -> str | None:
        """Enforce maximum comment length of 500 characters."""
        if v is not None and len(v) > 500:
            raise ValueError("Reviewer comment cannot exceed 500 characters.")
        return v


class HumanApprovalResult(BaseModel):
    """Authoritative Immutable Human Approval Result (Phase 310)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(..., description="Target approval request UUID")
    tenant_id: uuid.UUID = Field(..., description="Target tenant UUID")
    reviewer_id: uuid.UUID = Field(..., description="Authoritative human reviewer UUID")
    transaction_id: str = Field(..., description="Target transaction ID")
    status: ApprovalRequestStatus = Field(..., description="Updated request status (APPROVED)")
    decision: ApprovalDecisionType = Field(
        default=ApprovalDecisionType.APPROVE, description="Decision type"
    )
    decision_fingerprint: str = Field(..., description="SHA-256 fingerprint over approval decision")
    continuation_status: str | None = Field(
        default=None, description="Downstream Phase 309 continuation status if auto_continue=True"
    )
    is_existing: bool = Field(
        default=False, description="True if result was returned from idempotent replay cache"
    )
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Approval decision timestamp UTC",
    )
