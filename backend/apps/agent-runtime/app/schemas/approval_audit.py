"""Strongly typed schemas for Phase 308 — Approval Audit Subsystem."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.approval_request import ApprovalRequestStatus


class ApprovalAuditEventType(StrEnum):
    """Authoritative Audit Event Taxonomy (Phase 308)."""

    APPROVAL_REQUEST_CREATED = "APPROVAL_REQUEST_CREATED"
    APPROVAL_VIEWED = "APPROVAL_VIEWED"
    APPROVAL_APPROVED = "APPROVAL_APPROVED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    APPROVAL_CANCELLED = "APPROVAL_CANCELLED"
    APPROVAL_EXECUTION_STARTED = "APPROVAL_EXECUTION_STARTED"
    APPROVAL_EXECUTION_SUCCEEDED = "APPROVAL_EXECUTION_SUCCEEDED"
    APPROVAL_EXECUTION_FAILED = "APPROVAL_EXECUTION_FAILED"
    APPROVAL_EXECUTION_BLOCKED = "APPROVAL_EXECUTION_BLOCKED"
    APPROVAL_REPLAYED = "APPROVAL_REPLAYED"
    APPROVAL_CONFLICT = "APPROVAL_CONFLICT"
    APPROVAL_AUTHORIZATION_FAILED = "APPROVAL_AUTHORIZATION_FAILED"


class ApprovalAuditActorType(StrEnum):
    """Authoritative Audit Actor Category (Phase 308)."""

    SYSTEM = "SYSTEM"
    AGENT = "AGENT"
    REVIEWER = "REVIEWER"
    PAYMENT_ENGINE = "PAYMENT_ENGINE"


class ApprovalAuditEvent(BaseModel):
    """Immutable Audit Event Model (Phase 308).

    Zero secrets exposed! Excludes key_secret, webhook_secret, or provider tokens.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    audit_event_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique audit record UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant ID")
    approval_request_id: uuid.UUID = Field(..., description="Target approval request ID")
    transaction_id: str = Field(..., description="Target transaction ID")
    agent_id: uuid.UUID = Field(..., description="Target agent ID")
    event_type: ApprovalAuditEventType = Field(..., description="Categorized audit event type")
    actor_type: ApprovalAuditActorType = Field(..., description="Categorized actor type")
    actor_id: uuid.UUID | None = Field(
        default=None, description="UUID of actor (reviewer or agent)"
    )
    previous_status: ApprovalRequestStatus | None = Field(
        default=None, description="Prior approval status"
    )
    resulting_status: ApprovalRequestStatus | None = Field(
        default=None, description="Resulting approval status"
    )
    authorization_id: uuid.UUID | None = Field(
        default=None, description="Associated authorization ID"
    )
    authorization_fingerprint: str | None = Field(
        default=None, description="SHA-256 fingerprint over authorization"
    )
    approval_fingerprint: str = Field(..., description="SHA-256 fingerprint over approval request")
    timestamp_utc: datetime = Field(..., description="Server-authoritative UTC timestamp")
    event_fingerprint: str = Field(
        ..., description="SHA-256 SHA-256 tamper-evident fingerprint of event"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Safe key-value event metadata (zero secrets)"
    )


class ApprovalAuditQueryResult(BaseModel):
    """Query result envelope for audit logs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: uuid.UUID = Field(..., description="Target tenant ID")
    approval_request_id: uuid.UUID = Field(..., description="Target approval request ID")
    total_events: int = Field(..., description="Total audit events found")
    events: list[ApprovalAuditEvent] = Field(..., description="List of immutable audit records")
    all_events_verified: bool = Field(
        ..., description="True if all event fingerprints verify successfully"
    )
