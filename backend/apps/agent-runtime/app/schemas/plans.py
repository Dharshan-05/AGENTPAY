"""Pydantic Transport Schemas for Agent Planning (Phases 146–148)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class PlanStep(BaseModel):
    """Structured step representation in an agent plan (Phase 146)."""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(
        ...,
        description="Deterministic identifier for step (e.g. 'step-1')",
        pattern=r"^step-\d+$",
    )
    sequence: int = Field(..., ge=1, description="1-indexed sequence number")
    action: str = Field(..., description="Canonical step action name")
    target: str = Field(..., description="Target resource or entity description")
    description: str = Field(..., description="Human-readable step rationale")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    dependencies: list[str] = Field(
        default_factory=list, description="List of step_ids this step depends on"
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict, description="Step execution constraints"
    )
    expected_result: str = Field(..., description="Expected outcome description")
    risk_level: str = Field(
        default="low", description="Risk assessment: 'low', 'medium', 'high', 'critical'"
    )
    requires_authorization: bool = Field(
        default=False, description="Descriptive flag for authorization requirement"
    )
    requires_tool: bool = Field(
        default=False, description="Descriptive flag indicating tool requirement"
    )
    execution_eligible: bool = Field(
        default=True, description="Descriptive flag indicating execution eligibility"
    )


class PlanConstraints(BaseModel):
    """Constraints governing an agent plan (Phase 146)."""

    model_config = ConfigDict(extra="forbid")

    max_amount: Decimal | None = Field(
        default=None, description="Maximum monetary limit for plan execution"
    )
    allowed_currencies: list[str] = Field(
        default_factory=lambda: ["USD"], description="List of permitted ISO 4217 currencies"
    )
    timeout_seconds: int = Field(default=300, ge=1, description="Maximum execution duration")
    requires_human_approval: bool = Field(
        default=False, description="Flag for manual approval threshold"
    )
    risk_tolerance: str = Field(
        default="medium", description="Target risk tolerance: 'low', 'medium', 'high'"
    )


class PlanMetadata(BaseModel):
    """Explainability metadata for an agent plan (Phase 146)."""

    model_config = ConfigDict(extra="forbid")

    intent_category: str = Field(..., description="Canonical intent category")
    confidence: Decimal = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="Generated plan rationale")
    generator_version: str = Field(default="1.0.0", description="Planner algorithm version")
    planner_id: str = Field(default="deterministic_planner_v1", description="Planner component ID")


class AgentPlan(BaseModel):
    """Canonical Agent Plan Representation (Phase 146)."""

    model_config = ConfigDict(extra="forbid")

    plan_id: uuid.UUID = Field(..., description="Unique plan UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant ID scope")
    agent_id: uuid.UUID = Field(..., description="Agent ID scope")
    intent_id: uuid.UUID | None = Field(default=None, description="Associated intent ID")
    intent_type: str = Field(..., description="Associated intent category")
    version: str = Field(default="1.0.0", description="Plan specification version")
    status: str = Field(
        default="draft", description="Plan status: 'draft', 'ready', 'rejected', 'failed'"
    )
    steps: list[PlanStep] = Field(..., min_length=1, description="Ordered plan steps")
    constraints: PlanConstraints = Field(..., description="Governing plan constraints")
    metadata: PlanMetadata = Field(..., description="Planning explainability metadata")
    created_at: datetime = Field(..., description="Plan creation timestamp")


class AgentPlanCreateRequest(StrictRequestModel):
    """Request payload to generate a plan from stored/normalized intent (Phase 146).

    Rejects server-controlled fields (`tenant_id`, `agent_id`, `plan_id`, `created_at`, `status`).
    """

    intent_id: uuid.UUID | None = Field(
        default=None, description="ID of previously stored agent intent"
    )
    request_text: str | None = Field(
        default=None, description="Raw request text to extract/normalize/plan in one step"
    )
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context parameters"
    )


class AgentPlanResponse(BaseModel):
    """API Response model returning AgentPlan representation (Phase 146)."""

    model_config = ConfigDict(extra="forbid")

    plan_id: uuid.UUID
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    intent_id: uuid.UUID | None
    intent_type: str
    version: str
    status: str
    steps: list[PlanStep]
    constraints: PlanConstraints
    metadata: PlanMetadata
    created_at: datetime


class AgentPlanValidateRequest(StrictRequestModel):
    """Request payload to validate an existing plan representation (Phase 148)."""

    plan: AgentPlan = Field(..., description="Agent plan object to validate")


class PlanValidationResult(BaseModel):
    """Result model returned by Plan Validation (Phase 148)."""

    model_config = ConfigDict(extra="forbid")

    is_valid: bool = Field(..., description="True if plan satisfies all invariants")
    errors: list[str] = Field(default_factory=list, description="Validation error messages")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal validation warnings")
    execution_eligible: bool = Field(
        default=True, description="True if plan is safe and eligible for future execution"
    )
    validation_version: str = Field(default="1.0.0", description="Validator version")
