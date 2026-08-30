"""Pydantic Transport & Domain Schemas for Behaviour Risk Engine (Phase 211)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_risk_profile import RiskFactor


class BehaviourRiskRequest(BaseModel):
    """Payload contract for calculating normalized behaviour risk (Phase 211)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    amount: Decimal | None = Field(default=None, description="Proposed amount")
    currency: str = Field(default="USD", description="Proposed currency ISO code")
    merchant_id: uuid.UUID | None = Field(default=None, description="Proposed merchant UUID")
    category: str | None = Field(default=None, description="Proposed category")


class BehaviourRiskResult(BaseModel):
    """Structured outcome of Behaviour Risk calculation (Phase 211)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    behaviour_risk_score: Decimal = Field(
        ..., description="Bounded Decimal behaviour risk score (0.00 to 1.00)"
    )
    severity: str = Field(
        ..., description="Severity level (NORMAL, LOW, MEDIUM, HIGH, CRITICAL, COLD_START)"
    )
    risk_factors: list[RiskFactor] = Field(
        default_factory=list, description="List of behaviour risk factors"
    )
    confidence: Decimal = Field(
        ..., description="Confidence level in calculated score (0.00 to 1.00)"
    )
    explanation: str = Field(default="", description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
