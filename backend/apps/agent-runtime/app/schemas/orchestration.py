"""Pydantic Transport Schemas for Agent Orchestration (Phase 149)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class AgentOrchestrationCreateRequest(StrictRequestModel):
    """Request payload to initiate an orchestration decision (Phase 149).

    Rejects server-controlled fields (tenant_id, agent_id, orchestration_id, created_at, state).
    """

    intent_id: uuid.UUID | None = Field(default=None, description="Optional stored intent UUID")
    plan_id: uuid.UUID | None = Field(default=None, description="Optional validated plan UUID")
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context parameters"
    )


class AgentOrchestrationResponse(BaseModel):
    """Response model returning Agent Orchestration decision result (Phase 149)."""

    model_config = ConfigDict(extra="forbid")

    orchestration_id: uuid.UUID = Field(..., description="Unique orchestration UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant ID scope")
    agent_id: uuid.UUID = Field(..., description="Agent ID scope")
    intent_id: uuid.UUID | None = Field(default=None, description="Associated intent UUID")
    plan_id: uuid.UUID | None = Field(default=None, description="Associated plan UUID")
    state: str = Field(
        ...,
        description="Orchestration state: CREATED, VALIDATING, READY, BLOCKED, REJECTED, CANCELLED",
    )
    execution_eligible: bool = Field(
        ..., description="True if agent/plan is eligible for future execution phase"
    )
    decision: str = Field(..., description="Canonical decision outcome: READY, BLOCKED, REJECTED")
    blocking_reasons: list[str] = Field(
        default_factory=list, description="Detailed list of blocking or rejection reasons"
    )
    required_permissions: list[str] = Field(
        default_factory=list, description="List of permissions required for plan execution"
    )
    resolved_permissions: list[str] = Field(
        default_factory=list, description="List of effective agent permissions"
    )
    trust_status: str = Field(
        ..., description="Agent trust status ('high', 'medium', 'low', 'restricted')"
    )
    trust_score: Decimal = Field(..., description="Numerical trust score (0.00 to 100.00)")
    plan_valid: bool = Field(..., description="True if plan representation is valid")
    intent_valid: bool = Field(..., description="True if stored intent is valid")
    created_at: datetime = Field(..., description="Orchestration decision timestamp")
