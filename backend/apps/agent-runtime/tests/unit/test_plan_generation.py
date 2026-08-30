"""Unit & Security tests for Phase 147 — Plan Generation."""

import uuid
from decimal import Decimal

from app.application.services.plan_generation_service import PlanGenerationService
from app.schemas.agents import ExtractedEntities, StructuredIntent


def test_plan_generation_determinism() -> None:
    """Test plan generation is 100% deterministic given identical intent."""
    service = PlanGenerationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    intent_id = uuid.uuid4()

    intent = StructuredIntent(
        intent_id=intent_id,
        action="payment",
        confidence=Decimal("0.95"),
        source="rule_based",
        entities=ExtractedEntities(amount=Decimal("150.00"), currency="USD", merchant="cloud_corp"),
    )

    plan1 = service.generate_plan(
        tenant_id=tenant_id, agent_id=agent_id, intent=intent, intent_category="PAYMENT"
    )
    plan2 = service.generate_plan(
        tenant_id=tenant_id, agent_id=agent_id, intent=intent, intent_category="PAYMENT"
    )

    assert plan1.plan_id == plan2.plan_id
    assert len(plan1.steps) == len(plan2.steps)
    for s1, s2 in zip(plan1.steps, plan2.steps, strict=True):
        assert s1.step_id == s2.step_id
        assert s1.action == s2.action
        assert s1.inputs == s2.inputs


def test_payment_plan_generation_safety() -> None:
    """Test PAYMENT plan generates descriptive steps without execution side effects."""
    service = PlanGenerationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    intent_id = uuid.uuid4()

    intent = StructuredIntent(
        intent_id=intent_id,
        action="payment",
        confidence=Decimal("0.98"),
        source="rule_based",
        entities=ExtractedEntities(amount=Decimal("500.00"), currency="EUR", merchant="tech_corp"),
    )

    plan = service.generate_plan(
        tenant_id=tenant_id, agent_id=agent_id, intent=intent, intent_category="PAYMENT"
    )

    assert plan.intent_type == "PAYMENT"
    assert len(plan.steps) == 5
    assert plan.steps[0].action == "validate_intent"
    assert plan.steps[1].action == "lookup_merchant"
    assert plan.steps[2].action == "check_constraints"
    assert plan.steps[3].action == "request_authorization"
    assert plan.steps[4].action == "prepare_payment"

    # Descriptive flags check
    assert plan.steps[3].requires_authorization is True
    assert plan.steps[4].requires_tool is True


def test_unknown_intent_plan_generation() -> None:
    """Test UNKNOWN intent generates non-executable rejected plan representation."""
    service = PlanGenerationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    intent_id = uuid.uuid4()

    intent = StructuredIntent(
        intent_id=intent_id,
        action="unknown",
        confidence=Decimal("0.10"),
        source="rule_based",
        entities=ExtractedEntities(),
    )

    plan = service.generate_plan(
        tenant_id=tenant_id, agent_id=agent_id, intent=intent, intent_category="UNKNOWN"
    )

    assert plan.intent_type == "UNKNOWN"
    assert plan.status == "rejected"
    assert len(plan.steps) == 1
    assert plan.steps[0].action == "reject_unknown_intent"
    assert plan.steps[0].execution_eligible is False


def test_secret_sanitization_in_plan_generation() -> None:
    """Test secret material in raw strings is redacted during step generation."""
    service = PlanGenerationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    intent_id = uuid.uuid4()

    intent = StructuredIntent(
        intent_id=intent_id,
        action="lookup",
        confidence=Decimal("0.90"),
        source="rule_based",
        entities=ExtractedEntities(merchant="merchant_api_key: SecretKey999"),
    )

    plan = service.generate_plan(
        tenant_id=tenant_id, agent_id=agent_id, intent=intent, intent_category="MERCHANT_LOOKUP"
    )

    assert "SecretKey999" not in plan.steps[1].target
    assert "[REDACTED]" in plan.steps[1].target
