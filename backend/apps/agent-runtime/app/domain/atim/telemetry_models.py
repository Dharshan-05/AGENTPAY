"""ATIM Domain Telemetry & API Request/Response Schemas for AGENTPAY (Phase 10 / Group 5)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class ATIMTelemetryRecord(BaseModel):
    """Pydantic model representing an ATIM execution telemetry entry."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    request_id: Optional[uuid.UUID] = None

    prompt_text: Optional[str] = None
    action: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = "USD"

    is_security_blocked: bool = False
    security_score: Optional[Decimal] = None
    security_reason: Optional[str] = None

    selected_model: Optional[str] = None
    provider: Optional[str] = None
    fallback_used: bool = False

    task_type: Optional[str] = None
    complexity: Optional[str] = None
    risk_level: Optional[str] = None

    latency_ms: Optional[float] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: Decimal = Field(default=Decimal("0.000000"))

    agentguard_decision: Optional[str] = None
    fraudguard_score: Optional[float] = None
    hitl_required: bool = False
    execution_decision: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class LatencyDistribution(BaseModel):
    """Latency percentile metrics."""

    avg_ms: float = 0.0
    p50_ms: float = 0.0
    p75_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0


class ProviderCostAggregate(BaseModel):
    """Token and cost expenditure metrics per LLM provider/model."""

    provider: str
    model: str
    request_count: int = 0
    total_tokens: int = 0
    total_cost_usd: Decimal = Field(default=Decimal("0.000000"))


class ATIMTelemetryAggregate(BaseModel):
    """Aggregated telemetry summary for a tenant/global scope."""

    tenant_id: uuid.UUID
    total_requests: int = 0
    security_blocked_requests: int = 0
    security_block_rate: float = 0.0
    fallback_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: Decimal = Field(default=Decimal("0.000000"))
    latency_distribution: LatencyDistribution = Field(default_factory=LatencyDistribution)
    provider_breakdown: list[ProviderCostAggregate] = Field(default_factory=list)


class ATIMAnalyzeRequest(BaseModel):
    """Input payload for ATIM natural language transaction intelligence analysis."""

    prompt: str = Field(..., min_length=3, max_length=2048, description="User prompt or intent string")
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    requested_action: Optional[str] = Field(default=None, description="Explicit action hint if available")
    requested_amount: Optional[Decimal] = Field(default=None, description="Explicit amount hint if available")
    requested_currency: Optional[str] = Field(default="USD", description="Currency code")
    merchant_id: Optional[uuid.UUID] = None
    category: Optional[str] = None


class ATIMAnalyzeResponse(BaseModel):
    """Complete response payload for ATIM transaction intelligence analysis."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    agent_id: uuid.UUID

    prompt_security_blocked: bool
    security_reason: Optional[str] = None

    selected_model: str
    provider: str
    fallback_used: bool

    task_type: str
    complexity: str
    risk_level: str

    proposed_intent: Optional[Any] = None
    proposed_plan: Optional[Any] = None
    plan_valid: bool = False

    agentguard_decision: str
    fraudguard_score: float
    hitl_required: bool
    final_execution_decision: str

    latency_ms: float
    estimated_cost_usd: Decimal
