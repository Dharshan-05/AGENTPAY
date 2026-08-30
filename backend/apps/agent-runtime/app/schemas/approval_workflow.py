"""Pydantic Schemas for Approval Workflow Subsystem (Phase 305)."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.reviewer_authorization import TrustedReviewerContext


class ApprovalDecisionType(StrEnum):
    """Authoritative Approval Decision Type Enum (Phase 305)."""

    APPROVE = "APPROVE"


class ApprovalDecisionCommand(BaseModel):
    """Authoritative Command to Approve a Payment Approval Request (Phase 305).

    CRITICAL INVARIANTS:
    - Must specify decision = APPROVE (Phase 305 only handles approval).
    - Reviewer identity MUST originate from trusted session context.
    - Reviewer comment is bounded (Max 500 chars, no script injection).
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(
        ..., description="Target approval request UUID to approve"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context from session")
    reviewer_context: TrustedReviewerContext = Field(
        ..., description="Trusted reviewer identity & authorization context"
    )
    decision: ApprovalDecisionType = Field(
        default=ApprovalDecisionType.APPROVE,
        description="Approval decision (Must be APPROVE in Phase 305)",
    )
    reviewer_comment: str | None = Field(
        default=None, description="Optional bounded reviewer comment / justification"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")
    expected_approval_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint expected on target approval request"
    )

    @field_validator("reviewer_comment")
    @classmethod
    def validate_reviewer_comment_safe(cls, v: str | None) -> str | None:
        """Validate and sanitize reviewer comment."""
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        if len(cleaned) > 500:
            raise ValueError("Reviewer comment cannot exceed 500 characters.")
        # Reject dangerous executable/script tag injections
        if re.search(r"<script|javascript:|data:text/html", cleaned, re.IGNORECASE):
            raise ValueError("Reviewer comment contains forbidden executable script tags.")
        return cleaned


class ApprovalWorkflowResult(BaseModel):
    """Authoritative Immutable Outcome of Approval State Transition (Phase 305).

    CRITICAL: Does NOT trigger payment execution (Phase 309).
    Excludes provider credentials, secrets, or raw headers.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(..., description="Approved approval request UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    reviewer_id: uuid.UUID = Field(..., description="Approving reviewer UUID")
    previous_status: ApprovalRequestStatus = Field(
        default=ApprovalRequestStatus.PENDING, description="Status before transition"
    )
    new_status: ApprovalRequestStatus = Field(
        default=ApprovalRequestStatus.APPROVED, description="Status after transition"
    )
    decision: ApprovalDecisionType = Field(
        default=ApprovalDecisionType.APPROVE, description="Executed decision"
    )
    decision_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint over approval decision event"
    )
    is_existing: bool = Field(
        default=False, description="True if replayed existing approval result"
    )
    approved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Approval state mutation timestamp UTC",
    )
