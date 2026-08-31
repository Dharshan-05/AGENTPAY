"""ATIM Model Registry for managing typed model profiles, capabilities, and scores (Phase 9)."""

from __future__ import annotations

from decimal import Decimal
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("agentpay.atim.routing.registry")


class ModelProfile(BaseModel):
    """Profile describing an LLM provider model's capabilities and evaluation scores."""

    model_config = ConfigDict(extra="forbid")

    provider_name: str = Field(..., description="Provider name e.g. openai, anthropic")
    model_name: str = Field(..., description="Canonical model identifier e.g. gpt-4o, claude-3-5-sonnet")
    context_window: int = Field(default=128000, ge=1000)
    supports_structured_output: bool = Field(default=True)
    supports_tool_calling: bool = Field(default=True)
    supports_reasoning: bool = Field(default=False)

    security_score: Decimal = Field(default=Decimal("0.98"), ge=Decimal("0.0"), le=Decimal("1.0"))
    intent_score: Decimal = Field(default=Decimal("0.96"), ge=Decimal("0.0"), le=Decimal("1.0"))
    planning_score: Decimal = Field(default=Decimal("0.95"), ge=Decimal("0.0"), le=Decimal("1.0"))
    latency_score: Decimal = Field(default=Decimal("0.90"), ge=Decimal("0.0"), le=Decimal("1.0"))
    cost_score: Decimal = Field(default=Decimal("0.85"), ge=Decimal("0.0"), le=Decimal("1.0"))
    schema_score: Decimal = Field(default=Decimal("0.99"), ge=Decimal("0.0"), le=Decimal("1.0"))

    enabled: bool = Field(default=True)
    minimum_risk_level: str = Field(default="low", description="Supported minimum risk level: low, medium, high, critical")


class ATIMModelRegistry:
    """Registry maintaining available model profiles for deterministic intelligent routing."""

    def __init__(self) -> None:
        self._models: dict[str, ModelProfile] = {}
        self._register_default_models()

    def _register_default_models(self) -> None:
        """Populate initial production model profiles."""
        gpt4o = ModelProfile(
            provider_name="openai",
            model_name="gpt-4o",
            context_window=128000,
            supports_structured_output=True,
            supports_tool_calling=True,
            supports_reasoning=True,
            security_score=Decimal("0.98"),
            intent_score=Decimal("0.97"),
            planning_score=Decimal("0.96"),
            latency_score=Decimal("0.90"),
            cost_score=Decimal("0.80"),
            schema_score=Decimal("0.99"),
            enabled=True,
            minimum_risk_level="critical",
        )
        claude = ModelProfile(
            provider_name="anthropic",
            model_name="claude-3-5-sonnet-20241022",
            context_window=200000,
            supports_structured_output=True,
            supports_tool_calling=True,
            supports_reasoning=True,
            security_score=Decimal("0.97"),
            intent_score=Decimal("0.96"),
            planning_score=Decimal("0.95"),
            latency_score=Decimal("0.88"),
            cost_score=Decimal("0.75"),
            schema_score=Decimal("0.98"),
            enabled=True,
            minimum_risk_level="critical",
        )
        self.register_model(gpt4o)
        self.register_model(claude)

    def register_model(self, profile: ModelProfile) -> None:
        """Register or update a model profile in the registry."""
        key = f"{profile.provider_name}/{profile.model_name}"
        self._models[key] = profile
        logger.info("Registered model profile: %s (SecurityScore: %s)", key, profile.security_score)

    def get_model(self, provider_name: str, model_name: str) -> ModelProfile | None:
        """Retrieve profile by provider and model name."""
        key = f"{provider_name}/{model_name}"
        return self._models.get(key)

    def list_eligible_models(
        self,
        min_security_score: Decimal = Decimal("0.95"),
        min_schema_score: Decimal = Decimal("0.95"),
        requires_structured: bool = True,
    ) -> list[ModelProfile]:
        """Filter models passing hard security & capability eligibility floors."""
        eligible: list[ModelProfile] = []
        for profile in self._models.values():
            if not profile.enabled:
                continue
            if profile.security_score < min_security_score:
                continue
            if profile.schema_score < min_schema_score:
                continue
            if requires_structured and not profile.supports_structured_output:
                continue
            eligible.append(profile)
        return eligible
