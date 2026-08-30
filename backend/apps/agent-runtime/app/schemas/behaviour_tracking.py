"""Pydantic Transport & Domain Schemas for Behaviour Tracking (Phase 200)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BehaviourEvent(BaseModel):
    """Normalized representation of a recorded agent activity event (Phase 200)."""

    model_config = ConfigDict(extra="forbid")

    event_id: uuid.UUID = Field(..., description="Unique event identifier")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    event_type: str = Field(..., description="Event category (PAYMENT, TOOL_EXECUTION, etc.)")
    occurred_at: datetime = Field(..., description="Event timestamp in UTC")
    amount: Decimal | None = Field(default=None, description="Event monetary amount in Decimal")
    currency: str | None = Field(default=None, description="Event ISO currency code")
    merchant_id: uuid.UUID | None = Field(default=None, description="Associated Merchant UUID")
    category: str | None = Field(default=None, description="Associated product/event category")
    status: str = Field(..., description="Raw event status (completed, failed, etc.)")
    outcome: str = Field(..., description="Normalized outcome (SUCCESS, FAILED)")


class BehaviourTrackingQueryRequest(BaseModel):
    """Payload contract for querying historical agent behaviour events (Phase 200)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    event_type: str | None = Field(default=None, description="Optional event type filter")
    start_time: datetime | None = Field(default=None, description="Optional start datetime bound")
    end_time: datetime | None = Field(default=None, description="Optional end datetime bound")
    limit: int = Field(default=50, ge=1, le=100, description="Bounded limit (max 100)")


class BehaviourTrackingQueryResponse(BaseModel):
    """Paginated list of normalized agent behaviour events (Phase 200)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    events: list[BehaviourEvent] = Field(
        default_factory=list, description="List of normalized events"
    )
    total_count: int = Field(..., description="Total count of retrieved events")
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Query completion timestamp"
    )
