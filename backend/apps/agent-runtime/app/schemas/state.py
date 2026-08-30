"""Pydantic Transport Schemas for Agent Runtime State Management (Phase 150)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class AgentStateUpdateRequest(StrictRequestModel):
    """Request payload to request an agent runtime state transition (Phase 150).

    Rejects server-controlled fields (tenant_id, agent_id, previous_state, actor_id, timestamp).
    """

    requested_transition: str = Field(
        ...,
        description="Requested target state: IDLE, PREPARING, READY, BLOCKED, WAITING, FAILED",
    )
    reason: str | None = Field(
        default=None, max_length=500, description="Optional transition rationale"
    )


class AgentStateResponse(BaseModel):
    """Response model returning Agent Runtime State representation (Phase 150)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Agent UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    current_state: str = Field(
        ...,
        description="Current runtime state: IDLE, PREPARING, READY, BLOCKED, WAITING, FAILED",
    )
    previous_state: str | None = Field(
        default=None, description="Previous runtime state before last transition"
    )
    lifecycle_status: str = Field(
        ...,
        description="Authoritative lifecycle status ('active', 'paused', 'suspended')",
    )
    reason: str | None = Field(default=None, description="Last transition reason")
    updated_at: datetime = Field(..., description="State update timestamp")
