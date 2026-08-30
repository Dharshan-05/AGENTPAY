"""Pydantic Transport & Domain Schemas for Transaction Threshold Engine (Phase 191)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionThresholdEvaluationRequest(BaseModel):
    """Payload contract for transaction threshold evaluation (Phase 191)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    amount: Decimal = Field(..., description="Proposed transaction amount in Decimal")
    currency: str = Field(default="USD", description="Transaction currency ISO code")
    minimum_amount: Decimal | None = Field(
        default=None, description="Optional minimum transaction amount"
    )
    maximum_amount: Decimal | None = Field(
        default=None, description="Optional maximum hard denial transaction amount"
    )
    approval_threshold: Decimal | None = Field(
        default=None, description="Optional amount threshold requiring human approval"
    )
    threshold_currency: str = Field(default="USD", description="Configured threshold currency")
    enforcement_mode: str = Field(
        default="enforce", description="Enforcement mode (enforce, block, warn, monitor)"
    )


class TransactionThresholdEvaluationResult(BaseModel):
    """Structured outcome of evaluating a transaction threshold (Phase 191)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    amount: Decimal = Field(..., description="Proposed transaction amount")
    currency: str = Field(..., description="Transaction currency code")
    decision: str = Field(
        ..., description="Evaluation decision outcome (ALLOW, DENY, REQUIRE_APPROVAL)"
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation completion timestamp"
    )
