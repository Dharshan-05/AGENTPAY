"""ATIM Intelligent Model Router & Adaptive Inference Engine (Phase 9)."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
import logging
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.application.services.atim_circuit_breaker import ATIMCircuitBreaker
from app.application.services.atim_model_registry import ATIMModelRegistry, ModelProfile
from app.core.config import Settings

logger = logging.getLogger("agentpay.atim.routing.intelligent_router")


class RoutingTaskType(StrEnum):
    """Categorized task types for ATIM routing."""

    INTENT_EXTRACTION = "INTENT_EXTRACTION"
    CONSTRAINT_EXTRACTION = "CONSTRAINT_EXTRACTION"
    PLANNING = "PLANNING"
    REFUND_REASONING = "REFUND_REASONING"
    TRANSACTION_LOOKUP = "TRANSACTION_LOOKUP"
    SECURITY_SENSITIVE = "SECURITY_SENSITIVE"
    HIGH_RISK_FINANCIAL = "HIGH_RISK_FINANCIAL"
    GENERAL_AGENT_INTELLIGENCE = "GENERAL_AGENT_INTELLIGENCE"


class RequestComplexity(StrEnum):
    """Request complexity levels."""

    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"
    CRITICAL = "CRITICAL"


class RiskLevel(StrEnum):
    """Execution risk classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RoutingDecision(BaseModel):
    """Structured routing decision metadata."""

    model_config = ConfigDict(extra="forbid")

    routing_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID | None = Field(default=None)
    agent_id: uuid.UUID | None = Field(default=None)
    task_type: RoutingTaskType
    risk_level: RiskLevel
    complexity: RequestComplexity
    candidate_models_count: int
    eligible_models_count: int
    selected_provider: str
    selected_model: str
    selection_reasons: list[str] = Field(default_factory=list)
    security_floor_enforced: bool = Field(default=True)
    fallback_route: str | None = Field(default=None)


class ATIMIntelligentRouter:
    """Deterministic, risk-aware LLM router for AGENTPAY transactions."""

    def __init__(
        self,
        registry: ATIMModelRegistry | None = None,
        circuit_breaker: ATIMCircuitBreaker | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.registry = registry or ATIMModelRegistry()
        self.circuit_breaker = circuit_breaker or ATIMCircuitBreaker()
        self.settings = settings or Settings()

    def classify_request(
        self, prompt_text: str, context_metadata: dict[str, Any]
    ) -> tuple[RoutingTaskType, RequestComplexity, RiskLevel]:
        """Deterministically classify task type, complexity, and risk level from server metadata."""
        lower_prompt = prompt_text.lower()

        # 1. Determine Risk Level
        if any(w in lower_prompt for w in ["refund", "transfer", "withdraw", "payment", "buy", "purchase"]):
            if any(w in lower_prompt for w in ["50000", "100000", "large", "max"]):
                risk = RiskLevel.CRITICAL
            else:
                risk = RiskLevel.HIGH
        elif any(w in lower_prompt for w in ["balance", "status", "lookup", "search"]):
            risk = RiskLevel.LOW
        else:
            risk = RiskLevel.MEDIUM

        # 2. Determine Task Type
        if "refund" in lower_prompt:
            task = RoutingTaskType.REFUND_REASONING
        elif any(w in lower_prompt for w in ["buy", "purchase", "pay"]):
            task = RoutingTaskType.INTENT_EXTRACTION
        elif any(w in lower_prompt for w in ["plan", "step", "schedule"]):
            task = RoutingTaskType.PLANNING
        elif "lookup" in lower_prompt or "status" in lower_prompt:
            task = RoutingTaskType.TRANSACTION_LOOKUP
        else:
            task = RoutingTaskType.GENERAL_AGENT_INTELLIGENCE

        # 3. Determine Complexity
        word_count = len(prompt_text.split())
        if word_count > 30 or "and" in lower_prompt:
            complexity = RequestComplexity.COMPLEX
        elif word_count > 10:
            complexity = RequestComplexity.MODERATE
        else:
            complexity = RequestComplexity.SIMPLE

        return task, complexity, risk

    def route_request(
        self,
        prompt_text: str,
        tenant_id: uuid.UUID | None = None,
        agent_id: uuid.UUID | None = None,
        context_metadata: dict[str, Any] | None = None,
    ) -> RoutingDecision:
        """Route request to eligible model using deterministic risk-weighted scoring."""
        ctx = context_metadata or {}
        task, complexity, risk = self.classify_request(prompt_text, ctx)

        min_sec_score = Decimal(str(self.settings.atim_security_min_score))
        min_schema_score = Decimal(str(self.settings.atim_min_schema_validity))

        # Hard Eligibility Filter
        all_models = self.registry.list_eligible_models(
            min_security_score=min_sec_score,
            min_schema_score=min_schema_score,
        )

        eligible_models: list[ModelProfile] = []
        for model in all_models:
            if not self.circuit_breaker.is_available(model.provider_name):
                logger.info("Skipping model %s due to OPEN circuit breaker on provider", model.provider_name)
                continue
            eligible_models.append(model)

        if not eligible_models:
            logger.warning("No eligible models passed hard security/health filters. Falling back to primary configuration.")
            selected_provider = self.settings.llm_primary_provider
            selected_model = self.settings.llm_primary_model
            return RoutingDecision(
                tenant_id=tenant_id,
                agent_id=agent_id,
                task_type=task,
                risk_level=risk,
                complexity=complexity,
                candidate_models_count=len(all_models),
                eligible_models_count=0,
                selected_provider=selected_provider,
                selected_model=selected_model,
                selection_reasons=["Rule-engine / Primary fallback due to zero eligible models"],
                security_floor_enforced=True,
                fallback_route="rule_engine_fallback",
            )

        # Risk-Weighted Model Scoring
        scored_models: list[tuple[Decimal, ModelProfile]] = []
        for model in eligible_models:
            if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                # Security dominates for high-risk financial tasks
                sec_w, acc_w, cost_w = Decimal("0.60"), Decimal("0.30"), Decimal("0.10")
            else:
                sec_w, acc_w, cost_w = Decimal("0.30"), Decimal("0.40"), Decimal("0.30")

            score = (
                sec_w * model.security_score
                + acc_w * model.intent_score
                + cost_w * model.cost_score
            )
            scored_models.append((score, model))

        scored_models.sort(key=lambda x: x[0], reverse=True)
        winner_score, winner_model = scored_models[0]

        reasons = [
            f"Highest risk-weighted score ({winner_score:.2f})",
            f"Security floor satisfied ({winner_model.security_score} >= {min_sec_score})",
            f"Provider '{winner_model.provider_name}' circuit CLOSED",
        ]

        logger.info(
            "Routed request (Task: %s, Risk: %s) to %s/%s",
            task,
            risk,
            winner_model.provider_name,
            winner_model.model_name,
        )

        return RoutingDecision(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_type=task,
            risk_level=risk,
            complexity=complexity,
            candidate_models_count=len(all_models),
            eligible_models_count=len(eligible_models),
            selected_provider=winner_model.provider_name,
            selected_model=winner_model.model_name,
            selection_reasons=reasons,
            security_floor_enforced=True,
        )
