"""Pydantic Transport & Domain Schemas for Spending Limit Engine (Phase 189)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SpendingLimitEvaluationRequest(BaseModel):
    """Payload contract for single transaction spending limit check (Phase 189)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    amount: Decimal = Field(..., description="Proposed transaction amount in Decimal")
    currency: str = Field(default="USD", description="Currency ISO code")
    configured_limit: Decimal = Field(..., description="Configured limit in Decimal")
    limit_currency: str = Field(default="USD", description="Configured limit currency")
    enforcement_mode: str = Field(
        default="enforce", description="Enforcement mode (enforce, block, warn, monitor)"
    )


class SpendingLimitEvaluationResult(BaseModel):
    """Structured result of evaluating a proposed spending limit (Phase 189)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    amount: Decimal = Field(..., description="Proposed transaction amount")
    limit_amount: Decimal = Field(..., description="Configured limit amount")
    currency: str = Field(..., description="Evaluated currency ISO code")
    decision: str = Field(
        ...,
        description="Outcome decision (WITHIN_LIMIT, LIMIT_EXCEEDED, NO_LIMIT_CONFIGURED, INVALID_CURRENCY, INVALID_AMOUNT, REQUIRES_APPROVAL)",  # noqa: E501
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation completion timestamp"
    )
