"""Pydantic Transport & Domain Schemas for Merchant Behaviour Analysis (Phase 204)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MerchantBehaviourAnalysisRequest(BaseModel):
    """Payload contract for analyzing merchant-specific agent behaviour (Phase 204)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    merchant_id: uuid.UUID = Field(..., description="Target Merchant UUID")
    amount: Decimal | None = Field(default=None, description="Proposed transaction amount")
    currency: str = Field(default="USD", description="Proposed currency ISO code")


class MerchantBehaviourAnalysisResult(BaseModel):
    """Structured outcome of merchant behaviour analysis (Phase 204)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    merchant_id: uuid.UUID = Field(..., description="Target Merchant UUID")
    familiarity: str = Field(
        ..., description="Familiarity level (FAMILIAR, UNFAMILIAR, FIRST_SEEN, INSUFFICIENT_DATA)"
    )
    transaction_count: int = Field(..., description="Historical merchant transaction count")
    total_amount: Decimal = Field(..., description="Total historical merchant transaction amount")
    average_amount: Decimal = Field(..., description="Average historical merchant amount")
    merchant_share: Decimal = Field(
        ..., description="Merchant share of total transactions (0.00 to 1.00)"
    )
    severity: str = Field(
        ..., description="Severity level (NORMAL, LOW, MEDIUM, HIGH, CRITICAL, COLD_START)"
    )
    merchant_score: Decimal = Field(..., description="Merchant risk score (0.00 to 1.00 Decimal)")
    reason_codes: list[str] = Field(
        default_factory=list, description="Taxonomy of merchant risk reason codes"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
