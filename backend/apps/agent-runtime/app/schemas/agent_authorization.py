"""Pydantic Transport Schemas for Agent Authorization Subsystem (Phase 183)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentAuthorizationCheckRequest(BaseModel):
    """Payload for checking agent authorization for an operation (Phase 183)."""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., min_length=2, max_length=100, description="Target action or operation")
    resource_type: str | None = Field(default=None, description="Optional target resource type")
    resource_id: str | None = Field(default=None, description="Optional target resource ID")
    required_permissions: list[str] = Field(
        default_factory=list, description="Required permission names to check"
    )


class AgentAuthorizationResponse(BaseModel):
    """Deterministic authorization decision for an agent operation (Phase 183)."""

    model_config = ConfigDict(extra="forbid")

    allowed: bool = Field(..., description="True if operation is authorized; False otherwise")
    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    principal_id: uuid.UUID = Field(..., description="Authenticated principal UUID")
    action: str = Field(..., description="Action evaluated")
    decision_reason: str = Field(..., description="Rationale for authorization decision")
    evaluated_at: datetime = Field(..., description="Decision timestamp")
