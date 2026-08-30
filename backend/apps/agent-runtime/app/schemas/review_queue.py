"""Pydantic Schemas for Review Queue Backend Subsystem (Phase 303)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.approval_request import ApprovalRequestPriority, ApprovalRequestStatus
from app.schemas.payment import SupportedCurrency


class ReviewQueueQuery(BaseModel):
    """Authoritative Review Queue Filter & Keyset Pagination Query (Phase 303).

    Tenant context MUST originate from trusted session/authentication, never arbitrary user input.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(
        ..., description="Authoritative tenant UUID context from trusted auth"
    )
    status: ApprovalRequestStatus | None = Field(
        default=ApprovalRequestStatus.PENDING,
        description="Filter by approval status (Default PENDING)",
    )
    operation: str | None = Field(
        default=None, description="Optional filter by operation (e.g. REFUND, CANCEL, CREATE_ORDER)"
    )
    min_priority: ApprovalRequestPriority | None = Field(
        default=None, description="Optional minimum priority threshold filter"
    )
    created_after: datetime | None = Field(
        default=None, description="Filter for items created after timestamp UTC"
    )
    created_before: datetime | None = Field(
        default=None, description="Filter for items created before timestamp UTC"
    )

    page_size: int = Field(
        default=20, ge=1, le=100, description="Bounded page size (Max 100 items per page)"
    )
    cursor_created_at: datetime | None = Field(
        default=None, description="Keyset pagination cursor timestamp UTC"
    )
    cursor_id: uuid.UUID | None = Field(
        default=None, description="Keyset pagination cursor approval request UUID"
    )

    @field_validator("page_size")
    @classmethod
    def validate_page_size_bounded(cls, v: int) -> int:
        """Enforce page size limit to prevent unrestricted memory/query scans."""
        if v > 100:
            raise ValueError("Page size cannot exceed 100 items per page.")
        return v


class ReviewQueueItem(BaseModel):
    """Safe Public Review Queue Item Representation (Phase 303).

    Strictly excludes key_secret, webhook_secret, raw credentials, or authorization secrets!
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    approval_request_id: uuid.UUID = Field(..., description="Unique approval request UUID")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    order_id: str | None = Field(default=None, description="Razorpay order ID if available")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if available")

    amount: Decimal = Field(..., description="Financial payment amount (Decimal)")
    currency: SupportedCurrency = Field(..., description="Payment ISO currency code")
    operation: str = Field(..., description="Requested payment operation name")
    status: ApprovalRequestStatus = Field(..., description="Current request status")
    risk_score: float = Field(..., description="Composite risk score evaluated")
    priority: ApprovalRequestPriority = Field(..., description="Approval request priority")

    created_at: datetime = Field(..., description="Creation timestamp UTC")
    expires_at: datetime = Field(..., description="Expiration timestamp UTC")


class ReviewQueueResult(BaseModel):
    """Authoritative Review Queue Paginated Outcome Contract (Phase 303)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    items: list[ReviewQueueItem] = Field(..., description="Safe review queue item list")
    total_count: int = Field(..., ge=0, description="Total items matching filter in tenant")
    page_size: int = Field(..., description="Applied page size")
    next_cursor_created_at: datetime | None = Field(
        default=None, description="Next cursor created_at timestamp if more pages exist"
    )
    next_cursor_id: uuid.UUID | None = Field(
        default=None, description="Next cursor approval_request_id if more pages exist"
    )
    query_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint over query and page result metadata"
    )
