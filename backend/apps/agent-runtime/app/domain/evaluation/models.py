"""Domain Pydantic models for ATIM Phase 8 Evaluation & Benchmark Engine."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCase(BaseModel):
    """Single benchmark dataset evaluation test case."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique dataset test case ID e.g. INTENT-001")
    category: str = Field(default="intent_basic", description="Benchmark dataset category")
    input_text: str = Field(..., description="Raw input prompt text")
    expected_action: str | None = Field(default=None, description="Expected intent action")
    expected_amount: Decimal | None = Field(default=None, description="Expected Decimal amount")
    expected_currency: str | None = Field(default=None, description="Expected ISO currency")
    expected_merchant: str | None = Field(default=None, description="Expected merchant name")
    expected_is_ambiguous: bool = Field(default=False, description="Expected ambiguity flag")
    is_adversarial: bool = Field(default=False, description="True if prompt injection / adversarial test case")
    risk_level: str = Field(default="low", description="Associated risk classification")


class MetricResult(BaseModel):
    """Result of a single evaluated metric."""

    model_config = ConfigDict(extra="forbid")

    name: str
    score: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("1.0"))
    details: dict[str, Any] = Field(default_factory=dict)


class SecurityEvaluationResult(BaseModel):
    """Detailed security evaluation report."""

    model_config = ConfigDict(extra="forbid")

    attacks_tested: int = Field(default=0, ge=0)
    attacks_blocked: int = Field(default=0, ge=0)
    false_positives: int = Field(default=0, ge=0)
    block_rate: Decimal = Field(default=Decimal("1.0"), ge=Decimal("0.0"), le=Decimal("1.0"))
    false_positive_rate: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"), le=Decimal("1.0"))


class LatencyEvaluationResult(BaseModel):
    """Latency percentile metrics in milliseconds."""

    model_config = ConfigDict(extra="forbid")

    p50_ms: float = Field(default=0.0, ge=0.0)
    p75_ms: float = Field(default=0.0, ge=0.0)
    p90_ms: float = Field(default=0.0, ge=0.0)
    p95_ms: float = Field(default=0.0, ge=0.0)
    p99_ms: float = Field(default=0.0, ge=0.0)
    avg_ms: float = Field(default=0.0, ge=0.0)


class CostEvaluationResult(BaseModel):
    """Token consumption and financial cost calculation using Decimal."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: Decimal = Field(default=Decimal("0.0000"), ge=Decimal("0.0000"))


class ModelEligibility(BaseModel):
    """Evaluation decision declaring model eligibility for financial routing."""

    model_config = ConfigDict(extra="forbid")

    is_eligible: bool = Field(..., description="True if model satisfies all hard security & reliability floors")
    security_floor_passed: bool = Field(..., description="True if security_score >= 0.95")
    schema_floor_passed: bool = Field(..., description="True if schema_validity >= 0.95")
    failure_rate_passed: bool = Field(..., description="True if failure_rate <= 0.05")
    reasons: list[str] = Field(default_factory=list, description="Exclusion rationales if ineligible")


class EvaluationResult(BaseModel):
    """Single test case execution evaluation result."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    provider_name: str
    model_name: str
    passed: bool
    latency_ms: float
    intent_matched: bool = True
    entity_matched: bool = True
    constraint_matched: bool = True
    ambiguity_matched: bool = True
    plan_valid: bool = True
    security_blocked: bool = False
    schema_valid: bool = True
    error_message: str | None = None


class ModelScorecard(BaseModel):
    """Comprehensive composite scorecard for an LLM provider model."""

    model_config = ConfigDict(extra="forbid")

    provider_name: str
    model_name: str
    accuracy_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    constraint_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    plan_validity_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    security_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    reliability_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    latency_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    cost_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    composite_score: Decimal = Field(default=Decimal("1.00"), ge=Decimal("0.0"), le=Decimal("1.0"))
    eligibility: ModelEligibility
    latency_metrics: LatencyEvaluationResult = Field(default_factory=LatencyEvaluationResult)
    cost_metrics: CostEvaluationResult = Field(default_factory=CostEvaluationResult)
    security_metrics: SecurityEvaluationResult = Field(default_factory=SecurityEvaluationResult)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BenchmarkRun(BaseModel):
    """Complete benchmark execution run report."""

    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    dataset_name: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scorecards: list[ModelScorecard] = Field(default_factory=list)
