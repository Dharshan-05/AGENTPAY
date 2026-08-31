"""Domain models for ATIM Model Governance, Evaluation & Adaptive Routing (Phases 11 & 12)."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class GovernanceStatus(str, Enum):
    """Lifecycle states for LLM models under governance."""

    CANDIDATE = "CANDIDATE"
    EVALUATING = "EVALUATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    DEPRECATED = "DEPRECATED"
    ROLLED_BACK = "ROLLED_BACK"
    CHAMPION = "CHAMPION"


class EvaluationGate(str, Enum):
    """Gates required for model promotion."""

    SECURITY_FLOOR = "SECURITY_FLOOR"
    REGRESSION_TOLERANCE = "REGRESSION_TOLERANCE"
    GOVERNANCE_POLICY = "GOVERNANCE_POLICY"
    RBAC_AUTHORIZATION = "RBAC_AUTHORIZATION"


class ModelVersionRecord(BaseModel):
    """Immutable model version descriptor."""

    version_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    model_id: str
    provider_name: str
    version_tag: str
    commit_sha: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptVersionRecord(BaseModel):
    """Immutable prompt template version descriptor."""

    version_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    prompt_name: str
    version_tag: str
    template_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DatasetVersionRecord(BaseModel):
    """Immutable evaluation dataset version descriptor."""

    version_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    dataset_name: str
    version_tag: str
    case_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CompositeGovernanceScore(BaseModel):
    """Composite governance score blending accuracy, security, reliability, performance, and cost."""

    composite_score: float
    accuracy_score: float
    security_score: float
    reliability_score: float
    performance_score: float
    cost_score: float
    security_floor_passed: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GovernanceDecisionRecord(BaseModel):
    """Immutable governance decision audit record."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: Optional[uuid.UUID] = None
    actor_type: str = Field(default="SYSTEM", description="SYSTEM, ADMIN, USER")
    actor_id: Optional[uuid.UUID] = None
    model_id: str
    prompt_version: str = "v1.0.0"
    dataset_version: str = "v1.0.0"
    previous_status: GovernanceStatus
    new_status: GovernanceStatus
    decision_reason: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    security_score: Decimal = Field(default=Decimal("0.9500"))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CostBudgetRecord(BaseModel):
    """Cost budget quota configuration for tenant or agent."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    max_cost_per_request: Decimal = Field(default=Decimal("0.050000"))
    daily_budget_usd: Decimal = Field(default=Decimal("50.000000"))
    monthly_budget_usd: Decimal = Field(default=Decimal("1000.000000"))
    current_daily_spend_usd: Decimal = Field(default=Decimal("0.000000"))
    current_monthly_spend_usd: Decimal = Field(default=Decimal("0.000000"))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskPerformanceRecord(BaseModel):
    """Task-specific model performance metrics."""

    model_id: str
    task_type: str
    success_count: int = 0
    failure_count: int = 0
    quality_score: float = 1.0
    avg_latency_ms: float = 0.0
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RoutingExplanationRecord(BaseModel):
    """Auditable routing decision explanation object."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    selected_model: str
    provider: str
    task_type: str
    risk_level: str
    eligible_models: list[str]
    rejected_models: dict[str, str] = Field(default_factory=dict)
    routing_scores: dict[str, float] = Field(default_factory=dict)
    cost_estimate_usd: Decimal = Field(default=Decimal("0.000000"))
    latency_estimate_ms: float = 0.0
    security_score: Decimal = Field(default=Decimal("0.9500"))
    fallback_chain: list[str] = Field(default_factory=list)
    decision_reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
