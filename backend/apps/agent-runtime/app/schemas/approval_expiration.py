"""Strongly typed schemas for Phase 307 — Approval Expiration Subsystem."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.approval_request import ApprovalRequestStatus


class ApprovalExpirationCommand(BaseModel):
    """Command to evaluate and expire a payment approval request (Phase 307)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_request_id: uuid.UUID = Field(..., description="Target approval request ID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID")


class ApprovalExpirationResult(BaseModel):
    """Authoritative result of an approval request expiration evaluation (Phase 307)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_request_id: uuid.UUID = Field(..., description="Target approval request ID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID")
    previous_status: ApprovalRequestStatus = Field(..., description="Status prior to evaluation")
    resulting_status: ApprovalRequestStatus = Field(
        ..., description="Resulting status post-evaluation"
    )
    expired_at: datetime = Field(..., description="Server-authoritative UTC evaluation timestamp")
    is_expired: bool = Field(
        ..., description="True if status transition PENDING -> EXPIRED occurred"
    )
    is_existing: bool = Field(
        default=False, description="True if request was already in EXPIRED terminal state"
    )
    reason_code: str = Field(..., description="Explanation reason code for expiration outcome")
