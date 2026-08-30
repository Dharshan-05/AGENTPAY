"""Pydantic Transport Schemas for Agent Permission Evaluation Subsystem (Phase 184)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PermissionEvaluationRequest(BaseModel):
    """Payload requesting permission evaluation for an agent (Phase 184)."""

    model_config = ConfigDict(extra="forbid")

    requested_permissions: list[str] = Field(
        ..., min_length=1, description="List of canonical permission strings to evaluate"
    )
    principal_id: uuid.UUID | None = Field(
        default=None, description="Optional requesting user principal UUID"
    )


class PermissionEvaluationResult(BaseModel):
    """Deterministic permission evaluation result for an agent (Phase 184)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    principal_id: uuid.UUID | None = Field(default=None, description="Authenticated principal UUID")
    requested_permissions: list[str] = Field(
        ..., description="Complete set of requested permissions"
    )
    granted_permissions: list[str] = Field(
        ..., description="Permissions verified as granted to agent"
    )
    missing_permissions: list[str] = Field(
        ..., description="Permissions missing or denied for agent"
    )
    decision: str = Field(..., description="Overall decision (GRANTED, DENIED, UNKNOWN)")
    reason_code: str = Field(
        ..., description="Structured reason code (e.g. PERMISSION_GRANTED, PERMISSION_MISSING)"
    )
    evaluated_at: datetime = Field(..., description="Evaluation execution timestamp")
