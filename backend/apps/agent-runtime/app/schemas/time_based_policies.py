"""Pydantic Transport & Domain Schemas for Time-Based Policy Engine (Phase 194)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class TimeBasedPolicyEvaluationRequest(BaseModel):
    """Payload contract for time-based policy eligibility check (Phase 194)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    evaluation_time: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
    starts_at: datetime | None = Field(default=None, description="Effective start timestamp")
    ends_at: datetime | None = Field(default=None, description="Effective end timestamp")
    time_window_start: str | None = Field(
        default=None, description="Optional HH:MM start of daily time window"
    )
    time_window_end: str | None = Field(
        default=None, description="Optional HH:MM end of daily time window"
    )
    allowed_days: list[str] = Field(
        default_factory=list, description="List of allowed weekdays (monday, tuesday, etc.)"
    )
    timezone: str | None = Field(
        default="UTC", description="IANA timezone identifier (e.g. America/New_York)"
    )


class TimeBasedPolicyEvaluationResult(BaseModel):
    """Structured outcome of evaluating time-based eligibility (Phase 194)."""

    model_config = ConfigDict(extra="forbid")

    is_eligible: bool = Field(..., description="True if policy is currently active/eligible")
    window_type: str = Field(
        ...,
        description="Time window classification (ALWAYS_ACTIVE, DATE_RANGE, TIME_WINDOW, DAY_OF_WEEK, DATE_AND_TIME_WINDOW)",  # noqa: E501
    )
    reason_code: str = Field(..., description="Structured reason code flag")
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(..., description="Evaluation completion timestamp")
