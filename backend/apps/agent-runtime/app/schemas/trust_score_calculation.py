"""Pydantic Transport & Domain Schemas for Trust Score Calculation Engine (Phase 207)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_trust_score import TrustDimension


class TrustScoreCalculationRequest(BaseModel):
    """Payload contract for calculating trust score (Phase 207)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    behaviour_risk_score: Decimal = Field(
        default=Decimal("0.00"), description="Behaviour risk score (0.00 to 1.00)"
    )
    intent_risk_score: Decimal = Field(
        default=Decimal("0.00"), description="Intent risk score (0.00 to 1.00)"
    )
    velocity_risk_score: Decimal = Field(
        default=Decimal("0.00"), description="Velocity risk score (0.00 to 1.00)"
    )
    violation_count: int = Field(default=0, ge=0, description="Security violation count")
    baseline_available: bool = Field(
        default=True, description="True if historical baseline is available"
    )


class TrustScoreCalculationResult(BaseModel):
    """Structured outcome of trust score calculation (Phase 207)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    trust_score: Decimal = Field(..., description="Calculated trust score (0.00 to 1.00)")
    confidence: Decimal = Field(..., description="Overall score confidence (0.00 to 1.00)")
    trust_state: str = Field(..., description="Trust state classification")
    dimensions: list[TrustDimension] = Field(
        default_factory=list, description="List of evaluated trust dimensions"
    )
    deductions: dict[str, Decimal] = Field(
        default_factory=dict, description="Breakdown of deductions applied"
    )
    explanation: str = Field(..., description="Human-readable decision explanation")
    calculation_version: str = Field(default="2.0", description="Calculation engine version")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
