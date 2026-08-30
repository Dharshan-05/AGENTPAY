"""Pydantic Transport Schemas for Tool Permission System (Phase 158)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel
from app.schemas.tool_registry import ToolRiskClassification


class ToolAuthorizationDecisionEnum(StrEnum):
    """Deterministic authorization decision outcomes for tool execution (Phase 158)."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class ToolAuthorizationContext(BaseModel):
    """Context parameters evaluated by Tool Permission Engine (Phase 158)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    user_id: uuid.UUID | None = Field(default=None, description="Requesting User UUID")
    tool_id: str = Field(..., description="Target tool ID string")
    tool_version: str = Field(default="1.0.0", description="Tool version string")
    risk_classification: ToolRiskClassification = Field(
        default=ToolRiskClassification.LOW, description="Tool risk classification"
    )
    environment: str = Field(default="production", description="Target environment")
    amount: float | None = Field(
        default=None, ge=0.0, description="Transaction amount if financial"
    )  # noqa: E501
    currency: str = Field(default="USD", description="Currency code")
    action_name: str = Field(default="execute_tool", description="Requested action name")
    correlation_id: str | None = Field(default=None, description="Correlation tracing ID")


class ToolAuthorizationRequest(StrictRequestModel):
    """Request contract for pre-evaluating tool execution permission (Phase 158)."""

    agent_id: uuid.UUID = Field(..., description="Target agent UUID")
    tool_id: str = Field(..., min_length=2, max_length=100, description="Target tool ID")
    tool_version: str | None = Field(default=None, max_length=20, description="Optional version")
    amount: float | None = Field(default=None, ge=0.0, description="Optional transaction amount")
    currency: str = Field(default="USD", max_length=10, description="Currency code")
    environment: str = Field(default="production", max_length=50, description="Target environment")
    correlation_id: str | None = Field(default=None, max_length=100, description="Tracing ID")


class ToolAuthorizationResponse(BaseModel):
    """Response contract containing deterministic permission evaluation result (Phase 158)."""

    model_config = ConfigDict(extra="forbid")

    evaluation_id: uuid.UUID = Field(..., description="Unique evaluation session UUID")
    decision: ToolAuthorizationDecisionEnum = Field(..., description="Deterministic decision")
    tenant_id: uuid.UUID = Field(..., description="Tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    tool_id: str = Field(..., description="Tool ID")
    tool_version: str = Field(..., description="Tool version")
    reason: str = Field(..., description="Detailed rationale for decision")
    requires_approval: bool = Field(..., description="True if human approval is mandatory")
    approval_policy_name: str | None = Field(
        default=None, description="Matched approval policy name"
    )  # noqa: E501
    matched_permissions: list[str] = Field(
        default_factory=list, description="Evaluated permissions"
    )  # noqa: E501
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")
