"""Pydantic Transport & Domain Schemas for Velocity Detection Engine (Phase 203)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class VelocityDetectionRequest(BaseModel):
    """Payload contract for analyzing agent transaction velocity (Phase 203)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    window_start: datetime | None = Field(
        default=None, description="Start bound of analysis window"
    )
    window_end: datetime | None = Field(default=None, description="End bound of analysis window")
    window_minutes: int = Field(default=60, ge=1, le=1440, description="Window size in minutes")
    max_allowed_count: int | None = Field(
        default=None, description="Optional max transaction count threshold"
    )
    max_allowed_amount: Decimal | None = Field(
        default=None, description="Optional max total amount threshold"
    )


class VelocityDetectionResult(BaseModel):
    """Structured outcome of velocity analysis (Phase 203)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    window_start: datetime = Field(..., description="Effective window start timestamp")
    window_end: datetime = Field(..., description="Effective window end timestamp")
    transaction_count: int = Field(..., description="Observed transaction count in window")
    total_amount: Decimal = Field(..., description="Total transaction amount in window")
    transactions_per_minute: Decimal = Field(
        ..., description="Calculated transactions per minute rate"
    )
    transactions_per_hour: Decimal = Field(..., description="Calculated transactions per hour rate")
    baseline_available: bool = Field(..., description="True if baseline history was available")
    velocity_score: Decimal = Field(
        ..., description="Bounded velocity score (0.00 to 1.00 Decimal)"
    )
    severity: str = Field(
        ..., description="Severity (NORMAL, LOW, MEDIUM, HIGH, CRITICAL, INSUFFICIENT_DATA)"
    )
    detection_state: str = Field(
        ..., description="Detection state (NORMAL, VELOCITY_SPIKE, THRESHOLD_EXCEEDED)"
    )
    reason_codes: list[str] = Field(
        default_factory=list, description="Reason codes for detected velocity signals"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
