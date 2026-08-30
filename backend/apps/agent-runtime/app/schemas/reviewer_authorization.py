"""Pydantic Schemas for Reviewer Authorization Subsystem (Phase 304)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewerRole(StrEnum):
    """Authoritative Reviewer Role Enum (Phase 304)."""

    REVIEWER = "REVIEWER"
    SENIOR_REVIEWER = "SENIOR_REVIEWER"
    APPROVAL_ADMIN = "APPROVAL_ADMIN"


class ReviewerPermission(StrEnum):
    """Explicit Reviewer Capabilities Matrix (Phase 304)."""

    VIEW_APPROVAL_REQUEST = "reviews:read"
    VIEW_REVIEW_QUEUE = "reviews:queue_read"
    APPROVE_PAYMENT = "reviews:approve"
    REJECT_PAYMENT = "reviews:reject"
    CANCEL_APPROVAL = "reviews:cancel"
    VIEW_APPROVAL_AUDIT = "reviews:audit_read"


# Default monetary limits per role (in INR / base currency units)
DEFAULT_ROLE_LIMITS: dict[ReviewerRole, Decimal] = {
    ReviewerRole.REVIEWER: Decimal("50000.00"),
    ReviewerRole.SENIOR_REVIEWER: Decimal("500000.00"),
    ReviewerRole.APPROVAL_ADMIN: Decimal("10000000.00"),
}

DEFAULT_ROLE_PERMISSIONS: dict[ReviewerRole, set[ReviewerPermission]] = {
    ReviewerRole.REVIEWER: {
        ReviewerPermission.VIEW_APPROVAL_REQUEST,
        ReviewerPermission.VIEW_REVIEW_QUEUE,
        ReviewerPermission.APPROVE_PAYMENT,
        ReviewerPermission.REJECT_PAYMENT,
    },
    ReviewerRole.SENIOR_REVIEWER: {
        ReviewerPermission.VIEW_APPROVAL_REQUEST,
        ReviewerPermission.VIEW_REVIEW_QUEUE,
        ReviewerPermission.APPROVE_PAYMENT,
        ReviewerPermission.REJECT_PAYMENT,
        ReviewerPermission.CANCEL_APPROVAL,
    },
    ReviewerRole.APPROVAL_ADMIN: {
        ReviewerPermission.VIEW_APPROVAL_REQUEST,
        ReviewerPermission.VIEW_REVIEW_QUEUE,
        ReviewerPermission.APPROVE_PAYMENT,
        ReviewerPermission.REJECT_PAYMENT,
        ReviewerPermission.CANCEL_APPROVAL,
        ReviewerPermission.VIEW_APPROVAL_AUDIT,
    },
}


class TrustedReviewerContext(BaseModel):
    """Trusted Reviewer Identity & Authorization Context (Phase 304).

    MUST originate from trusted authentication context (session/bearer token).
    Client-supplied identity MUST NOT override authenticated identity.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    reviewer_id: uuid.UUID = Field(..., description="Authoritative human reviewer UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
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

    @field_validator("authorization_limit")
    @classmethod
    def validate_limit_positive(cls, v: Decimal) -> Decimal:
        """Validate non-negative approval limit."""
        if v.is_nan() or v.is_infinite():
            raise ValueError("Authorization limit cannot be NaN or Infinity.")
        if v < Decimal("0"):
            raise ValueError("Authorization limit cannot be negative.")
        return v


class ReviewerAuthorizationResult(BaseModel):
    """Authoritative Immutable Reviewer Authorization Outcome (Phase 304).

    Zero secrets exposed! Excludes credentials, raw headers, or provider tokens.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    authorized: bool = Field(..., description="True if reviewer is authorized to proceed")
    reviewer_id: uuid.UUID = Field(..., description="Target reviewer UUID")
    tenant_id: uuid.UUID = Field(..., description="Target tenant UUID")
    approval_request_id: uuid.UUID = Field(..., description="Target approval request UUID")
    permission: ReviewerPermission = Field(..., description="Requested permission evaluated")
    reason_code: str = Field(
        ..., description="Standard reason code (e.g. AUTHORIZATION_GRANTED, CROSS_TENANT_ACCESS)"
    )
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint over authorization decision"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Authorization evaluation timestamp UTC",
    )
