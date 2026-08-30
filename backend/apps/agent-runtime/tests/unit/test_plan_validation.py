"""Unit & Security tests for Phase 148 — Plan Validation."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.application.services.plan_validation_service import PlanValidationService
from app.schemas.plans import AgentPlan, PlanConstraints, PlanMetadata, PlanStep


def test_valid_plan_validation_success() -> None:
    """Test validating a well-formed AgentPlan succeeds fail-closed."""
    service = PlanValidationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    steps = [
        PlanStep(
            step_id="step-1",
            sequence=1,
            action="validate_intent",
            target="intent",
            description="Validate intent",
            expected_result="OK",
        ),
        PlanStep(
            step_id="step-2",
            sequence=2,
            action="query_account_balance",
            target="account",
            description="Query balance",
            dependencies=["step-1"],
            expected_result="OK",
        ),
    ]

    plan = AgentPlan(
        plan_id=plan_id,
        tenant_id=tenant_id,
        agent_id=agent_id,
        intent_type="BALANCE_QUERY",
        steps=steps,
        constraints=PlanConstraints(),
        metadata=PlanMetadata(
            intent_category="BALANCE_QUERY",
            confidence=Decimal("0.95"),
            rationale="Test plan",
        ),
        created_at=datetime.now(UTC),
    )

    res = service.validate_plan(plan, target_tenant_id=tenant_id, target_agent_id=agent_id)
    assert res.is_valid is True
    assert res.execution_eligible is True
    assert len(res.errors) == 0


def test_validation_rejects_duplicate_step_ids() -> None:
    """Test plan with duplicate step IDs fails validation."""
    service = PlanValidationService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    steps = [
        PlanStep(
            step_id="step-1",
            sequence=1,
            action="validate_intent",
            target="t1",
            description="d1",
            expected_result="OK",
        ),
        PlanStep(
            step_id="step-1",
            sequence=2,
            action="query_account_balance",
            target="t2",
            description="d2",
            expected_result="OK",
        ),
    ]

    plan = AgentPlan(
        plan_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        intent_type="BALANCE_QUERY",
        steps=steps,
        constraints=PlanConstraints(),
        metadata=PlanMetadata(
            intent_category="BALANCE_QUERY", confidence=Decimal("0.9"), rationale="r"
        ),
        created_at=datetime.now(UTC),
    )

    res = service.validate_plan(plan)
    assert res.is_valid is False
    assert any("Duplicate step_id" in err for err in res.errors)


def test_validation_rejects_cyclic_dependencies() -> None:
    """Test plan with cyclic step dependencies fails validation."""
    service = PlanValidationService()

    steps = [
        PlanStep(
            step_id="step-1",
            sequence=1,
            action="validate_intent",
            target="t1",
            description="d1",
            dependencies=["step-2"],
            expected_result="OK",
        ),
        PlanStep(
            step_id="step-2",
            sequence=2,
            action="check_constraints",
            target="t2",
            description="d2",
            dependencies=["step-1"],
            expected_result="OK",
        ),
    ]

    plan = AgentPlan(
        plan_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        intent_type="PAYMENT",
        steps=steps,
        constraints=PlanConstraints(),
        metadata=PlanMetadata(intent_category="PAYMENT", confidence=Decimal("0.9"), rationale="r"),
        created_at=datetime.now(UTC),
    )

    res = service.validate_plan(plan)
    assert res.is_valid is False


def test_validation_detects_secret_leakage() -> None:
    """Test plan with forbidden secret string in steps fails validation."""
    service = PlanValidationService()

    steps = [
        PlanStep(
            step_id="step-1",
            sequence=1,
            action="validate_intent",
            target="target_api_key: SuperSecretPassword123",
            description="Validate intent",
            expected_result="OK",
        )
    ]

    plan = AgentPlan(
        plan_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        intent_type="PAYMENT",
        steps=steps,
        constraints=PlanConstraints(),
        metadata=PlanMetadata(intent_category="PAYMENT", confidence=Decimal("0.9"), rationale="r"),
        created_at=datetime.now(UTC),
    )

    res = service.validate_plan(plan)
    assert res.is_valid is False
    assert any("Secret material detected" in err for err in res.errors)
