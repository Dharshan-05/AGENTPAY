"""Pydantic Transport & Domain Schemas for Intent Risk Engine (Phase 213)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_risk_profile import RiskFactor


class IntentRiskRequest(BaseModel):
    """Payload contract for calculating normalized intent risk (Phase 213)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    declared_intent: dict[str, Any] | None = Field(
        default=None, description="Raw declared intent dictionary"
    )
    requested_action: str = Field(default="payment", description="Requested action string")
    requested_amount: Decimal | None = Field(default=None, description="Requested amount")
    requested_currency: str = Field(default="USD", description="Requested currency ISO code")
    requested_merchant_id: str | None = Field(
        default=None, description="Requested merchant UUID/slug"
    )
    requested_category: str | None = Field(default=None, description="Requested category")


class IntentRiskResult(BaseModel):
    """Structured outcome of Intent Risk calculation (Phase 213)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    intent_risk_score: Decimal = Field(
        ..., description="Bounded Decimal intent risk score (0.00 to 1.00)"
    )
    severity: str = Field(
        ...,
        description="Severity level (VERIFIED, LOW_RISK, ELEVATED_RISK, HIGH_RISK, CRITICAL_RISK, DENIED)",  # noqa: E501
    )
    risk_factors: list[RiskFactor] = Field(
        default_factory=list, description="List of intent risk factors"
    )
    can_proceed: bool = Field(
        ..., description="False if critical mismatch renders execution unsafe"
    )
    explanation: str = Field(default="", description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
