"""Pydantic Transport & Domain Schemas for Agent Violation Tracking (Phase 209)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentViolation(BaseModel):
    """Structured security policy violation record (Phase 209)."""

    model_config = ConfigDict(extra="forbid")

    violation_id: uuid.UUID = Field(..., description="Unique violation identifier")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    violation_type: str = Field(..., description="Violation category code")
    severity: str = Field(..., description="Severity (LOW, MEDIUM, HIGH, CRITICAL)")
    occurred_at: datetime = Field(..., description="Violation timestamp in UTC")
    source: str = Field(..., description="Source subsystem")
    status: str = Field(default="ACTIVE", description="Violation status")
    recurrence_count: int = Field(default=1, ge=1, description="Deterministic recurrence count")
    policy_id: uuid.UUID | None = Field(
        default=None, description="Associated Security Policy UUID if applicable"
    )


class AgentViolationQueryRequest(BaseModel):
    """Payload contract for querying agent violations (Phase 209)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    limit: int = Field(default=50, ge=1, le=100, description="Bounded query limit")


class AgentViolationQueryResponse(BaseModel):
    """Paginated response for agent violations query (Phase 209)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    violations: list[AgentViolation] = Field(
        default_factory=list, description="List of recorded violations"
    )
    total_count: int = Field(..., description="Total count of violations")
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Retrieval timestamp"
    )
