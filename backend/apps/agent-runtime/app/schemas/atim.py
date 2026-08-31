"""ATIM (AgentPay Transaction Intelligence Model) Pydantic schemas."""

from __future__ import annotations

import uuid
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ToolRiskLevel(StrEnum):
    """Execution risk classification for proposed tools."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    PROPOSAL_ONLY = "proposal_only"


class ATIMConstraint(BaseModel):
    """Normalized operational constraint extracted by ATIM."""

    name: str = Field(description="Constraint name e.g. min_rating, max_price, brand")
    operator: str = Field(
        default="eq",
        description="Operator e.g. eq, lte, gte, lt, gt, in, contains, not_in",
    )
    value: Any = Field(description="Normalized constraint value")
    is_security_authoritative: bool = Field(
        default=False,
        description="Indicates whether this constraint is governed by AGENTGUARD server policy",
    )


class ATIMProposedIntent(BaseModel):
    """LLM-proposed structured intent payload prior to server policy evaluation."""

    intent_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    action: str = Field(
        description="Canonical intent action: PAYMENT, REFUND, TRANSACTION_LOOKUP, BALANCE_QUERY, MERCHANT_LOOKUP, USER_LOOKUP, AGENT_OPERATION, PRODUCT_SEARCH, PRODUCT_COMPARE"
    )
    target: str | None = Field(default=None, description="Target resource or entity identifier")
    amount: Decimal | None = Field(
        default=None, description="Extracted monetary amount in Decimal format"
    )
    currency: str | None = Field(
        default="USD", description="ISO 4217 currency code e.g. USD, INR, EUR"
    )
    merchant: str | None = Field(default=None, description="Target merchant name or ID")
    recipient: str | None = Field(default=None, description="Target recipient user or ID")
    category: str | None = Field(default=None, description="Product/service category")
    product: str | None = Field(default=None, description="Product or item search target")
    brand: str | None = Field(default=None, description="Target brand constraint e.g. Logitech")
    transaction_ref: str | None = Field(
        default=None, description="Transaction ID or reference number"
    )
    quantity: int = Field(default=1, ge=1, description="Requested item quantity")
    optimization: str | None = Field(
        default=None, description="Optimization target e.g. MIN_PRICE, MAX_RATING, CHEAPEST"
    )
    temporal_constraint: str | None = Field(
        default=None, description="Temporal phrase e.g. yesterday, today, this month"
    )
    negations: list[str] = Field(
        default_factory=list, description="Negated exclusions e.g. refurbished, amazon"
    )
    conditions: list[str] = Field(
        default_factory=list, description="Conditional constraints e.g. final_price_includes_shipping"
    )
    is_ambiguous: bool = Field(
        default=False, description="True if financial intent lacks mandatory attributes"
    )
    ambiguity_reason: str | None = Field(default=None, description="Explanation of ambiguity")
    missing_fields: list[str] = Field(
        default_factory=list, description="List of missing financial/product fields"
    )
    confidence_level: str = Field(
        default="HIGH_CONFIDENCE",
        description="Completeness level: HIGH_CONFIDENCE, LOW_CONFIDENCE, AMBIGUOUS, INVALID",
    )
    sub_intents: list[str] = Field(
        default_factory=list, description="Multi-intent decomposition e.g. SEARCH, FILTER, COMPARE, PURCHASE"
    )
    constraints: list[ATIMConstraint] = Field(
        default_factory=list, description="Extracted constraints"
    )
    confidence: Decimal = Field(
        default=Decimal("0.95"),
        ge=Decimal("0.00"),
        le=Decimal("1.00"),
        description="Model extraction confidence score between 0 and 1",
    )
    source: str = Field(default="atim_llm_v1", description="Source extraction model or engine")
    schema_version: str = Field(default="1.0.0", description="ATIM intent schema version")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str:
        if not v:
            return "USD"
        clean = v.upper().strip()
        if len(clean) != 3:
            raise ValueError(f"Invalid ISO 4217 currency code '{v}'")
        return clean

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        clean = v.upper().strip()
        supported = {
            "PAYMENT",
            "PURCHASE",
            "BUY",
            "REFUND",
            "TRANSACTION_LOOKUP",
            "BALANCE_QUERY",
            "MERCHANT_LOOKUP",
            "USER_LOOKUP",
            "AGENT_OPERATION",
            "PRODUCT_SEARCH",
            "PRODUCT_COMPARE",
        }

        if clean not in supported:
            return "UNKNOWN"
        return clean


class ToolProposal(BaseModel):
    """Proposal-only representation of a tool call emitted by ATIM."""

    tool_name: str = Field(description="Canonical tool identifier e.g. product.search")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Tool execution arguments"
    )
    sequence: int = Field(default=1, ge=1, description="Contiguous execution sequence number")
    risk_level: ToolRiskLevel = Field(
        default=ToolRiskLevel.LOW, description="Proposed tool risk classification"
    )
    is_financial: bool = Field(
        default=False, description="True if tool involves financial movement"
    )
    depends_on: list[str] = Field(
        default_factory=list, description="List of step IDs this tool step depends on"
    )
    requires_server_validation: bool = Field(
        default=True,
        description="Mandates AGENTGUARD and PlanValidationService verification prior to execution",
    )


class ATIMPlanProposal(BaseModel):
    """LLM-proposed multi-step transaction plan before server authorization."""

    plan_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    intent_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    proposed_intent: ATIMProposedIntent | None = Field(default=None)
    plan: Any = Field(default=None)
    proposed_tools: list[ToolProposal] = Field(default_factory=list)


    rationale: str = Field(
        default="ATIM dynamic plan proposal",
        description="Natural language rationale for the proposed sequence",
    )
    estimated_operations: int = Field(default=1, ge=1, description="Estimated total operations")
    risk_classification: str = Field(
        default="medium", description="Overall plan risk classification: low, medium, high, critical"
    )
    is_executable_proposal: bool = Field(
        default=True,
        description="False if unknown actions, ambiguity, or security risks were detected",
    )


class ATIMValidationResult(BaseModel):
    """Validation report generated when verifying ATIM proposals against server contracts."""

    is_valid: bool = Field(description="True if proposal satisfies schema & security constraints")
    errors: list[str] = Field(default_factory=list, description="Validation failure messages")
    warnings: list[str] = Field(default_factory=list, description="Validation warning messages")
    failover_recommended: bool = Field(
        default=False, description="True if LLM response required rule engine fallback"
    )

