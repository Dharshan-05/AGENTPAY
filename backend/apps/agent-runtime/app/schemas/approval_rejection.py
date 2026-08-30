"""Strongly typed schemas for Phase 306 — Approval Rejection Workflow."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.approval_request import ApprovalRequestStatus
from app.schemas.reviewer_authorization import TrustedReviewerContext


class RejectionReason(StrEnum):
    """Authoritative rejection reason taxonomy."""

    HIGH_RISK_SUSPECTED = "HIGH_RISK_SUSPECTED"
    UNAUTHORIZED_TRANSACTION = "UNAUTHORIZED_TRANSACTION"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    DUPLICATE_REQUEST = "DUPLICATE_REQUEST"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    SUSPICIOUS_AGENT_BEHAVIOR = "SUSPICIOUS_AGENT_BEHAVIOR"
    OTHER = "OTHER"


class ApprovalRejectionCommand(BaseModel):
    """Immutable command to reject a payment approval request (Phase 306)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_request_id: uuid.UUID = Field(..., description="Target approval request ID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID from session")
    reviewer_context: TrustedReviewerContext = Field(
        ..., description="Trusted reviewer identity and capability context"
    )
    rejection_reason: RejectionReason = Field(..., description="Categorized rejection reason")
    reviewer_comment: str | None = Field(
        default=None, description="Optional reviewer comment (max 500 chars)"
    )
    idempotency_key: str = Field(..., description="Caller idempotency key")
    expected_approval_fingerprint: str = Field(
        ..., description="Expected SHA-256 fingerprint on target request"
    )

    @field_validator("reviewer_comment")
    @classmethod
    def validate_reviewer_comment(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v_stripped = v.strip()
        if len(v_stripped) > 500:
            raise ValueError("Reviewer comment cannot exceed 500 characters.")
        # Reject malicious script tags or HTML injection strings
        if re.search(r"<\s*script", v_stripped, re.IGNORECASE) or re.search(
            r"javascript:", v_stripped, re.IGNORECASE
        ):
            raise ValueError("Reviewer comment contains forbidden executable script tags.")
        return v_stripped


class ApprovalRejectionResult(BaseModel):
    """Authoritative result of an approval rejection operation (Phase 306)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_request_id: uuid.UUID = Field(..., description="Target approval request ID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID")
    transaction_id: str = Field(..., description="Associated transaction ID")
    reviewer_id: uuid.UUID = Field(..., description="Reviewer user ID")
    previous_status: ApprovalRequestStatus = Field(
        ..., description="Status prior to rejection (MUST be PENDING)"
    )
    resulting_status: ApprovalRequestStatus = Field(
        ..., description="Resulting status (MUST be REJECTED)"
    )
    rejection_reason: RejectionReason = Field(..., description="Categorized rejection reason")
    decision_fingerprint: str = Field(..., description="SHA-256 decision fingerprint")
    processed_at: datetime = Field(..., description="UTC timestamp of decision execution")
    is_existing: bool = Field(
        default=False, description="True if result was returned from idempotency cache"
    )
