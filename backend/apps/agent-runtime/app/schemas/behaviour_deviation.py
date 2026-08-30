"""Pydantic Transport & Domain Schemas for Behaviour Deviation Engine (Phase 202)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.behaviour_baseline import BehaviourBaseline


class BehaviourDeviationRequest(BaseModel):
    """Payload contract for evaluating requested operation against behaviour baseline (Phase 202)."""  # noqa: E501

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    amount: Decimal | None = Field(default=None, description="Proposed transaction amount")
    currency: str = Field(default="USD", description="Proposed currency ISO code")
    merchant_id: uuid.UUID | None = Field(default=None, description="Proposed Merchant UUID")
    category: str | None = Field(default=None, description="Proposed category name")
    baseline: BehaviourBaseline = Field(..., description="Calculated behaviour baseline")


class BehaviourDeviationResult(BaseModel):
    """Structured outcome of evaluating behaviour deviation (Phase 202)."""

    model_config = ConfigDict(extra="forbid")

    has_deviation: bool = Field(
        ..., description="True if any significant behaviour deviation was detected"
    )
    severity: str = Field(
        ..., description="Deviation severity (NORMAL, LOW, MEDIUM, HIGH, CRITICAL, COLD_START)"
    )
    deviation_score: Decimal = Field(
        ..., description="Deviation score (0.00 to 1.00 Decimal precision)"
    )
    reason_codes: list[str] = Field(
        default_factory=list, description="Taxonomy of detected deviation reason codes"
    )
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation completion timestamp"
    )
