"""Unit tests for Phase 9 Model Registry."""

from decimal import Decimal
import pytest

from app.application.services.atim_model_registry import ATIMModelRegistry, ModelProfile


def test_01_model_registry_initialization_and_lookup():
    registry = ATIMModelRegistry()

    gpt4o = registry.get_model("openai", "gpt-4o")
    assert gpt4o is not None
    assert gpt4o.provider_name == "openai"
    assert gpt4o.security_score >= Decimal("0.95")


def test_02_model_registry_eligibility_filtering():
    registry = ATIMModelRegistry()

    # Register an ineligible model
    ineligible = ModelProfile(
        provider_name="test",
        model_name="ineligible-model",
        security_score=Decimal("0.80"),  # Below 0.95 floor
        enabled=True,
    )
    registry.register_model(ineligible)

    eligible = registry.list_eligible_models(min_security_score=Decimal("0.95"))
    model_names = [m.model_name for m in eligible]

    assert "gpt-4o" in model_names
    assert "ineligible-model" not in model_names
