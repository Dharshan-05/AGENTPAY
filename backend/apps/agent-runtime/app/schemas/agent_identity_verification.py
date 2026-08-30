"""Pydantic Transport Schemas for Agent Identity Verification Subsystem (Phase 182)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentIdentityVerificationRequest(BaseModel):
    """Payload for verifying an agent identity (Phase 182)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID | None = Field(
        default=None, description="Optional target Agent UUID if not passed in URL"
    )
    principal_id: uuid.UUID | None = Field(
        default=None, description="Optional requesting user principal UUID to check"
    )


class AgentIdentityVerificationResult(BaseModel):
    """Verified identity outcome for an agent (Phase 182)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    authenticated_principal_id: uuid.UUID | None = Field(
        default=None, description="Authenticated principal UUID"
    )
    verified: bool = Field(
        ..., description="True if agent exists, belongs to tenant, and is active"
    )
    agent_status: str = Field(..., description="Current agent status (active, paused, etc.)")
    verification_reason: str = Field(..., description="Human-readable verification explanation")
    verified_at: datetime = Field(..., description="Verification execution timestamp")
