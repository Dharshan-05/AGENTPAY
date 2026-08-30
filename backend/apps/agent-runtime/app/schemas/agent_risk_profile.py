"""Pydantic Transport & Domain Schemas for Agent Risk Profile Engine (Phase 208)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RiskFactor(BaseModel):
    """Structured risk factor representation (Phase 208)."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Risk factor code")
    severity: str = Field(..., description="Risk severity (LOW, MEDIUM, HIGH, CRITICAL)")
    source: str = Field(..., description="Signal source subsystem (BEHAVIOUR, INTENT, VELOCITY)")
    confidence: Decimal = Field(
        default=Decimal("1.00"), description="Confidence in factor (0.00 to 1.00)"
    )


class AgentRiskProfile(BaseModel):
    """Aggregated Agent Risk Profile representation (Phase 208)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    risk_score: Decimal = Field(
        ..., description="Calculated overall Decimal risk score (0.00 to 1.00)"
    )
    trust_score: Decimal = Field(..., description="Current Decimal trust score (0.00 to 1.00)")
    risk_level: str = Field(
        ..., description="Overall risk level (LOW, NORMAL, ELEVATED, HIGH, CRITICAL, COLD_START)"
    )
    risk_factors: list[RiskFactor] = Field(
        default_factory=list, description="List of contributing risk factors"
    )
    recommended_action: str = Field(
        default="ALLOW", description="Recommended action (ALLOW, REQUIRE_APPROVAL, DENY)"
    )
    explainable_reasons: list[str] = Field(
        default_factory=list, description="Human-readable decision explanation items"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
