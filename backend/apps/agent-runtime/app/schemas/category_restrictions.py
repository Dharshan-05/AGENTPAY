"""Pydantic Transport & Domain Schemas for Category Restriction Engine (Phase 192)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryRestrictionEvaluationRequest(BaseModel):
    """Payload contract for category restriction evaluation (Phase 192)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    category: str | None = Field(default=None, description="Target product/merchant category")
    allowed_categories: list[str] = Field(
        default_factory=list, description="Allowlist of permitted categories"
    )
    blocked_categories: list[str] = Field(
        default_factory=list, description="Denylist of blocked categories"
    )


class CategoryRestrictionEvaluationResult(BaseModel):
    """Structured outcome of evaluating a category restriction (Phase 192)."""

    model_config = ConfigDict(extra="forbid")

    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    category: str | None = Field(default=None, description="Target category evaluated")
    decision: str = Field(
        ..., description="Evaluation decision outcome (ALLOW, DENY, REQUIRE_APPROVAL)"
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Evaluation completion timestamp"
    )
