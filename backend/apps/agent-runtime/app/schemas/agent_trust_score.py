"""Pydantic Transport & Domain Schemas for Agent Trust Score (Phase 206)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TrustDimension(BaseModel):
    """Individual trust scoring dimension representation (Phase 206)."""

    model_config = ConfigDict(extra="forbid")

    dimension_name: str = Field(..., description="Name of the trust dimension")
    score: Decimal = Field(..., description="Decimal dimension score (0.00 to 1.00)")
    weight: Decimal = Field(..., description="Decimal dimension weight (0.00 to 1.00)")
    confidence: Decimal = Field(..., description="Decimal confidence score (0.00 to 1.00)")
    explanation: str = Field(..., description="Dimension evaluation explanation")
    source: str = Field(..., description="Signal source subsystem")


class AgentTrustScore(BaseModel):
    """Structured Agent Trust Score representation (Phase 206)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    trust_score: Decimal = Field(
        ..., description="Bounded trust score from 0.00 to 1.00 Decimal precision"
    )
    confidence: Decimal = Field(
        default=Decimal("1.00"), description="Overall confidence score (0.00 to 1.00)"
    )
    trust_state: str = Field(
        ...,
        description="State (TRUSTED, NORMAL, LOW_TRUST, HIGH_RISK, CRITICAL_RISK, COLD_START)",
    )
    dimensions: list[TrustDimension] = Field(
        default_factory=list, description="Breakdown of trust dimensions"
    )
    score_version: str = Field(default="2.0", description="Trust score schema version")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
    contributing_signal_summary: dict[str, str] = Field(
        default_factory=dict, description="Summary of contributing risk/trust signals"
    )
