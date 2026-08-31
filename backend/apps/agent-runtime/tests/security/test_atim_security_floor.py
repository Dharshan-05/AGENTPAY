"""Security test suite verifying hard security floor enforcement in routing (Phase 9)."""

from decimal import Decimal
import pytest

from app.application.services.atim_intelligent_router import ATIMIntelligentRouter
from app.application.services.atim_model_registry import ATIMModelRegistry, ModelProfile


def test_01_models_below_security_floor_never_selected():
    registry = ATIMModelRegistry()

    # Register cheap model with low security score (0.70 < 0.95 floor)
    cheap_insecure = ModelProfile(
        provider_name="budget_llm",
        model_name="insecure-cheap-v1",
        security_score=Decimal("0.70"),
        cost_score=Decimal("1.00"),
        enabled=True,
    )
    registry.register_model(cheap_insecure)

    router = ATIMIntelligentRouter(registry=registry)

    # Simple request where cost weight might normally favor cheap model
    decision = router.route_request("What is my balance?")

    assert decision.selected_provider != "budget_llm"
    assert decision.selected_model != "insecure-cheap-v1"
    assert decision.security_floor_enforced is True
