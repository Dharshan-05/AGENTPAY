"""Pydantic Transport & Domain Schemas for Agent Security History Engine (Phase 210)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentSecurityHistorySummary(BaseModel):
    """Aggregated Agent Security History representation (Phase 210)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_events: int = Field(..., description="Total count of historical security events")
    denial_count: int = Field(..., description="Count of policy denials")
    violation_count: int = Field(..., description="Count of policy violations")
    mismatch_count: int = Field(..., description="Count of intent mismatches")
    recent_severity_distribution: dict[str, int] = Field(
        default_factory=dict, description="Distribution of severities"
    )
    historical_trend: str = Field(
        default="STABLE", description="Historical trend (STABLE, DETERIORATING, IMPROVING)"
    )
    unresolved_incidents: int = Field(
        default=0, description="Count of unresolved active violations"
    )
    timeline_summary: list[dict[str, str]] = Field(
        default_factory=list, description="Recent event timeline items"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
