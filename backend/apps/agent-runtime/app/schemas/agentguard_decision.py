"""Pydantic Transport & Domain Schemas for AgentGuard Decision Engine (Phase 214)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_risk_profile import RiskFactor


class AgentGuardDecisionRequest(BaseModel):
    """Payload contract for full AGENTGUARD security decision (Phase 214)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    principal_id: uuid.UUID | None = Field(default=None, description="Authenticated principal UUID")
    transaction_id: uuid.UUID | None = Field(default=None, description="Transaction UUID")
    merchant_id: uuid.UUID | None = Field(default=None, description="Merchant UUID")
    category: str | None = Field(default=None, description="Category name")
    amount: Decimal | None = Field(default=None, description="Monetary amount in Decimal")
    currency: str = Field(default="USD", description="Currency ISO code")
    requested_action: str = Field(default="payment", description="Requested action string")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")


class AgentGuardDecisionResult(BaseModel):
    """Structured final outcome of AGENTGUARD Decision Engine (Phase 214)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    decision: str = Field(
        ...,
        description="Final decision (DENIED, REQUIRE_APPROVAL, ALLOW, REVIEW, REPLAN_REQUIRED, NO_APPLICABLE_POLICY)",  # noqa: E501
    )
    risk_level: str = Field(
        ..., description="Risk level (LOW, NORMAL, ELEVATED, HIGH, CRITICAL, COLD_START)"
    )
    risk_score: Decimal = Field(
        default=Decimal("0.00"), description="Calculated Decimal risk score (0.00 to 1.00)"
    )
    trust_score: Decimal = Field(..., description="Decimal trust score (0.00 to 1.00)")
    confidence: Decimal = Field(
        default=Decimal("1.00"), description="Overall decision confidence (0.00 to 1.00)"
    )
    behaviour_risk_score: Decimal = Field(..., description="Behaviour risk score (0.00 to 1.00)")
    velocity_risk_score: Decimal = Field(..., description="Velocity risk score (0.00 to 1.00)")
    intent_risk_score: Decimal = Field(..., description="Intent risk score (0.00 to 1.00)")
    can_proceed: bool = Field(..., description="True if operation may proceed")
    requires_approval: bool = Field(
        ..., description="True if operation requires explicit human approval"
    )
    reason_codes: list[str] = Field(
        default_factory=list, description="All aggregated decision reason codes"
    )
    blocking_factors: list[str] = Field(
        default_factory=list, description="Explicit factors forcing a DENY decision"
    )
    risk_factors: list[RiskFactor] = Field(
        default_factory=list, description="Aggregated risk factors"
    )
    evaluation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique evaluation execution UUID"
    )
    decision_version: str = Field(default="2.0", description="Decision engine version")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
