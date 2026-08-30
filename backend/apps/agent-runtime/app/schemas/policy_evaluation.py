"""Pydantic Transport Schemas for Policy Evaluation Engine (Phase 187)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PolicyEvaluationContext(BaseModel):
    """Extensible evaluation context payload for Policy Engine (Phase 187)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID | None = Field(default=None, description="Tenant scope UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Target Agent UUID")
    principal_id: uuid.UUID | None = Field(
        default=None, description="Optional requesting user principal UUID"
    )
    transaction_id: uuid.UUID | None = Field(default=None, description="Optional transaction UUID")
    merchant_id: uuid.UUID | None = Field(default=None, description="Optional merchant UUID")
    category: str | None = Field(default=None, description="Optional product/merchant category")
    amount: Decimal | None = Field(default=None, description="Transaction amount in Decimal")
    currency: str = Field(default="USD", description="Currency ISO code")
    requested_action: str = Field(default="transaction", description="Target action/operation")
    tool_name: str | None = Field(default=None, description="Optional tool name if tool execution")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Safe metadata (zero secrets)"
    )


class PolicyEvaluationResult(BaseModel):
    """Deterministic policy evaluation result (Phase 187)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    decision: str = Field(
        ...,
        description="Evaluation decision (ALLOW, DENY, REQUIRE_APPROVAL, NO_APPLICABLE_POLICY)",  # noqa: E501
    )
    evaluated_policy_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of all policies evaluated"
    )
    matched_policy_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of policies that matched context"
    )
    denied_policy_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of policies causing denial"
    )
    reason_codes: list[str] = Field(
        default_factory=list, description="Structured reason code flags"
    )
    decision_reason: str = Field(..., description="Human-readable decision explanation")
    highest_priority: int = Field(default=0, description="Highest policy priority evaluated")
    evaluated_at: datetime = Field(..., description="Evaluation completion timestamp")
