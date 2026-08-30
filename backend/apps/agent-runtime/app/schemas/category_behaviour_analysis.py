"""Pydantic Transport & Domain Schemas for Category Behaviour Analysis (Phase 205)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryBehaviourAnalysisRequest(BaseModel):
    """Payload contract for analyzing category-specific agent behaviour (Phase 205)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    category: str = Field(..., description="Target category name or path")
    amount: Decimal | None = Field(default=None, description="Proposed transaction amount")
    currency: str = Field(default="USD", description="Proposed currency ISO code")


class CategoryBehaviourAnalysisResult(BaseModel):
    """Structured outcome of category behaviour analysis (Phase 205)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    category: str = Field(..., description="Original requested category")
    normalized_category: str = Field(..., description="Normalized category string")
    familiarity: str = Field(
        ..., description="Familiarity level (FAMILIAR, UNFAMILIAR, FIRST_SEEN, INSUFFICIENT_DATA)"
    )
    transaction_count: int = Field(..., description="Historical category transaction count")
    total_amount: Decimal = Field(..., description="Total historical category transaction amount")
    average_amount: Decimal = Field(..., description="Average historical category amount")
    category_share: Decimal = Field(
        ..., description="Category share of total transactions (0.00 to 1.00)"
    )
    severity: str = Field(
        ..., description="Severity level (NORMAL, LOW, MEDIUM, HIGH, CRITICAL, COLD_START)"
    )
    category_score: Decimal = Field(..., description="Category risk score (0.00 to 1.00 Decimal)")
    reason_codes: list[str] = Field(
        default_factory=list, description="Taxonomy of category risk reason codes"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
