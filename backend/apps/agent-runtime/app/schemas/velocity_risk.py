"""Pydantic Transport & Domain Schemas for Velocity Risk Engine (Phase 212)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_risk_profile import RiskFactor


class VelocityRiskRequest(BaseModel):
    """Payload contract for calculating normalized velocity risk (Phase 212)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    window_minutes: int = Field(default=60, ge=1, le=1440, description="Analysis window in minutes")
    max_allowed_count: int | None = Field(
        default=None, description="Optional max allowed count threshold"
    )
    max_allowed_amount: Decimal | None = Field(
        default=None, description="Optional max allowed total amount"
    )


class VelocityRiskResult(BaseModel):
    """Structured outcome of Velocity Risk calculation (Phase 212)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    velocity_risk_score: Decimal = Field(
        ..., description="Bounded Decimal velocity risk score (0.00 to 1.00)"
    )
    severity: str = Field(..., description="Severity level (NORMAL, ELEVATED, HIGH, CRITICAL)")
    burst_detected: bool = Field(
        default=False, description="True if short-window activity burst detected"
    )
    window_minutes: int = Field(..., description="Observation window size in minutes")
    risk_factors: list[RiskFactor] = Field(
        default_factory=list, description="List of velocity risk factors"
    )
    explanation: str = Field(default="", description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
