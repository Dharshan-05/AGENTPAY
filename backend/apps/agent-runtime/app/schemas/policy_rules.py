"""Pydantic Transport & Domain Schemas for Policy Rule Engine (Phase 188)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PolicyRuleContext(BaseModel):
    """Evaluation context for a policy rule (Phase 188)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    principal_id: uuid.UUID | None = Field(default=None, description="Optional principal user UUID")
    transaction_id: uuid.UUID | None = Field(default=None, description="Optional transaction UUID")
    merchant_id: uuid.UUID | None = Field(default=None, description="Optional merchant UUID")
    category: str | None = Field(default=None, description="Optional category string")
    amount: Decimal | None = Field(
        default=None, description="Monetary transaction amount in Decimal"
    )
    currency: str = Field(default="USD", description="Currency ISO code")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation timestamp"
    )
    requested_action: str = Field(default="transaction", description="Requested action/operation")
    tool_name: str | None = Field(default=None, description="Optional tool name")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Safe context metadata (zero secrets)"
    )


class PolicyRuleResult(BaseModel):
    """Structured outcome of evaluating a policy rule (Phase 188)."""

    model_config = ConfigDict(extra="forbid")

    rule_id: uuid.UUID | None = Field(default=None, description="Evaluated rule UUID")
    rule_type: str = Field(..., description="Classification rule type")
    outcome: str = Field(
        ..., description="Evaluation outcome (MATCH, NO_MATCH, DENY, REQUIRE_APPROVAL, ERROR)"
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable evaluation explanation")
    evaluated_at: datetime = Field(..., description="Evaluation completion timestamp")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Audit safe metadata (zero secrets)"
    )
