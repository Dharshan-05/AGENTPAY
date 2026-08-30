"""Pydantic Transport & Domain Schemas for Merchant Restriction Engine (Phase 193)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class MerchantRestrictionEvaluationRequest(BaseModel):
    """Payload contract for merchant restriction evaluation (Phase 193)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    merchant_id: uuid.UUID | None = Field(default=None, description="Target Merchant UUID")
    merchant_slug: str | None = Field(default=None, description="Optional target merchant slug")
    allowed_merchants: list[str] = Field(
        default_factory=list, description="Allowlist of merchant UUIDs or slugs"
    )
    blocked_merchants: list[str] = Field(
        default_factory=list, description="Denylist of merchant UUIDs or slugs"
    )


class MerchantRestrictionEvaluationResult(BaseModel):
    """Structured outcome of evaluating a merchant restriction (Phase 193)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    merchant_id: uuid.UUID | None = Field(
        default=None, description="Target Merchant UUID evaluated"
    )  # noqa: E501
    decision: str = Field(
        ..., description="Evaluation decision outcome (ALLOW, DENY, REQUIRE_APPROVAL)"
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation completion timestamp"
    )
