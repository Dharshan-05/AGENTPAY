"""Pydantic Transport & Domain Schemas for Daily Spending Limit Engine (Phase 190)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DailySpendingLimitResult(BaseModel):
    """Structured outcome of evaluating daily cumulative spending limit (Phase 190)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    daily_limit: Decimal = Field(..., description="Configured daily limit amount in Decimal")
    current_usage: Decimal = Field(..., description="Current daily cumulative spending usage")
    requested_amount: Decimal = Field(..., description="Proposed transaction amount")
    projected_usage: Decimal = Field(
        ..., description="Projected cumulative usage after transaction"
    )  # noqa: E501
    remaining_limit: Decimal = Field(..., description="Remaining available limit for today")
    currency: str = Field(..., description="Currency ISO code")
    decision: str = Field(
        ...,
        description="Outcome decision (WITHIN_LIMIT, LIMIT_EXCEEDED, REQUIRES_APPROVAL, INVALID_CURRENCY, NO_LIMIT_CONFIGURED)",  # noqa: E501
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluation_period_start: datetime = Field(..., description="Start of daily evaluation window")
    evaluation_period_end: datetime = Field(..., description="End of daily evaluation window")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation completion timestamp"
    )
