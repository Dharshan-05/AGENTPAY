"""Unit and Security Tests for Policy Rule Engine (Phase 188)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.policy_rule_engine import PolicyRuleEngine
from app.infrastructure.database.models.policy_rule import PolicyRule
from app.schemas.policy_rules import PolicyRuleContext


@pytest.fixture
def engine() -> PolicyRuleEngine:
    return PolicyRuleEngine()


def test_01_evaluate_rule_equals_match(engine: PolicyRuleEngine) -> None:
    """1. Test rule evaluation with equality operator matching context."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    rule = PolicyRule(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        security_policy_id=uuid.uuid4(),
        name="Category Rule",
        slug="category-rule",
        status="active",
        rule_type="product",
        priority=100,
        operator="eq",
        condition_payload={"field": "category", "value": "electronics"},
        action="deny",
    )

    ctx = PolicyRuleContext(
        tenant_id=tenant_id, agent_id=agent_id, category="electronics", amount=Decimal("100.00")
    )
    res = engine.evaluate_rule(rule, ctx)
    assert res.outcome == "DENY"
    assert res.reason_code == "RULE_MATCH_CATEGORY-RULE"


def test_02_evaluate_rule_numeric_greater_than_match(engine: PolicyRuleEngine) -> None:
    """2. Test numeric comparison operator gt."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    rule = PolicyRule(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        security_policy_id=uuid.uuid4(),
        name="Amount Threshold",
        slug="amount-threshold",
        status="active",
        rule_type="amount",
        priority=100,
        operator="gt",
        condition_payload={"field": "amount", "value": "500.00"},
        action="require_approval",
    )

    ctx = PolicyRuleContext(tenant_id=tenant_id, agent_id=agent_id, amount=Decimal("600.00"))
    res = engine.evaluate_rule(rule, ctx)
    assert res.outcome == "REQUIRE_APPROVAL"


def test_03_unknown_operator_fails_closed_error(engine: PolicyRuleEngine) -> None:
    """3. Test unknown operator fails closed with ERROR result."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    rule = PolicyRule(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        security_policy_id=uuid.uuid4(),
        name="Unknown Operator Rule",
        slug="unknown-operator-rule",
        status="active",
        rule_type="custom",
        priority=100,
        operator="unknown_eval_hack",
        condition_payload={"field": "amount", "value": "100"},
        action="deny",
    )

    ctx = PolicyRuleContext(tenant_id=tenant_id, agent_id=agent_id, amount=Decimal("100.00"))
    res = engine.evaluate_rule(rule, ctx)
    assert res.outcome == "ERROR"
    assert res.reason_code == "UNKNOWN_OPERATOR"
