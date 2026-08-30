"""Pydantic Transport & Domain Schemas for Behaviour Baseline Engine (Phase 201)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AmountStatistics(BaseModel):
    """Monetary amount statistical summary in Decimal precision (Phase 201)."""

    model_config = ConfigDict(extra="forbid")

    total_amount: Decimal = Field(..., description="Sum of all transaction amounts")
    average_amount: Decimal = Field(..., description="Mean transaction amount")
    min_amount: Decimal = Field(..., description="Minimum transaction amount")
    max_amount: Decimal = Field(..., description="Maximum transaction amount")


class BehaviourBaseline(BaseModel):
    """Structured behavioural baseline computed from historical activity (Phase 201)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    baseline_available: bool = Field(
        ..., description="True if sufficient historical observations exist"
    )
    state: str = Field(
        ..., description="Baseline state (COLD_START, INSUFFICIENT_HISTORY, ESTABLISHED)"
    )  # noqa: E501
    observation_count: int = Field(..., description="Total count of observed events")
    successful_count: int = Field(..., description="Count of successful events")
    failed_count: int = Field(..., description="Count of failed events")
    amount_stats: AmountStatistics | None = Field(
        default=None, description="Amount statistics if observations exist"
    )
    frequent_merchants: list[str] = Field(
        default_factory=list, description="Top merchant UUIDs/slugs"
    )
    frequent_categories: list[str] = Field(
        default_factory=list, description="Top product categories"
    )
    frequent_currencies: list[str] = Field(default_factory=list, description="Top currencies used")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Baseline generation timestamp"
    )
