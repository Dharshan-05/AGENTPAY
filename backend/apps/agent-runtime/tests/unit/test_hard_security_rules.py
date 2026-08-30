"""Unit & Mandatory Security Tests for Hard Security Rule Configurations & Schemas (Phase 277)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.risk.hard_security_rules import HardSecurityRulesEngine
from app.schemas.risk_engine import (
    HardSecurityRuleConfiguration,
    HardSecurityRuleOutcome,
    HardSecurityRuleSeverity,
    HardSecurityRuleType,
    RiskEvaluationContext,
)


def _make_context(
    t_id: uuid.UUID | None = None,
    a_id: uuid.UUID | None = None,
    tx_id: str = "tx_001",
    ts: datetime | None = None,
) -> RiskEvaluationContext:
    return RiskEvaluationContext(
        tenant_id=t_id or uuid.uuid4(),
        agent_id=a_id or uuid.uuid4(),
        transaction_id=tx_id,
        prediction_timestamp=ts or datetime.now(UTC),
    )


def test_01_default_hard_security_rules_initialization() -> None:
    """1. Test default hard security rules engine initialization."""
    engine = HardSecurityRulesEngine()
    assert len(engine.rules) == 8
    rule_types = {r.rule_type for r in engine.rules}
    assert HardSecurityRuleType.POLICY_DENY in rule_types
    assert HardSecurityRuleType.TARGET_LEAKAGE in rule_types


def test_02_duplicate_rule_id_rejection() -> None:
    """2. Mandatory Security Test: Duplicate rule_id in config fails closed."""
    dup_rule1 = HardSecurityRuleConfiguration(
        rule_id="HSR-999",
        rule_type=HardSecurityRuleType.VELOCITY_VIOLATION,
    )
    dup_rule2 = HardSecurityRuleConfiguration(
        rule_id="HSR-999",  # Duplicate rule_id!
        rule_type=HardSecurityRuleType.SECURITY_INVARIANT,
    )

    with pytest.raises(ValueError, match="Duplicate rule_id"):
        HardSecurityRulesEngine(rules=[dup_rule1, dup_rule2])


def test_03_future_effective_date_rule_config_rejection() -> None:
    """3. Mandatory Temporal Security Test: Future effective_from rule config fails closed."""
    now = datetime.now(UTC)
    ctx = _make_context(ts=now)
    future_from = datetime(2030, 1, 1, tzinfo=UTC)

    future_rule = HardSecurityRuleConfiguration(
        rule_id="HSR-888",
        rule_type=HardSecurityRuleType.SECURITY_INVARIANT,
        effective_from=future_from,
    )

    engine = HardSecurityRulesEngine(rules=[future_rule])
    with pytest.raises(ValueError, match="is in the future relative to prediction timestamp"):
        engine._validate_rules([future_rule], context=ctx)


def test_04_tenant_mismatch_rule_config_rejection() -> None:
    """4. Mandatory Security Test: Tenant mismatch in rule configuration fails closed."""
    ctx = _make_context()
    other_tenant = uuid.uuid4()

    tenant_rule = HardSecurityRuleConfiguration(
        rule_id="HSR-777",
        rule_type=HardSecurityRuleType.SECURITY_INVARIANT,
        tenant_id=other_tenant,  # Cross-tenant config attack!
    )

    engine = HardSecurityRulesEngine(rules=[tenant_rule])
    with pytest.raises(ValueError, match="Tenant ID mismatch in rule config"):
        engine._validate_rules([tenant_rule], context=ctx)


def test_05_deterministic_rule_config_hash() -> None:
    """5. Test rule configuration hash determinism."""
    rule1 = HardSecurityRuleConfiguration(
        rule_id="HSR-001",
        rule_type=HardSecurityRuleType.POLICY_DENY,
    )
    rule2 = HardSecurityRuleConfiguration(
        rule_id="HSR-001",
        rule_type=HardSecurityRuleType.POLICY_DENY,
    )

    assert rule1.compute_hash() == rule2.compute_hash()


def test_06_rule_types_enums_coverage() -> None:
    """6. Test HardSecurityRuleType, Severity, and Outcome enums."""
    assert HardSecurityRuleSeverity.CRITICAL.value == "CRITICAL"
    assert HardSecurityRuleOutcome.TRIGGERED.value == "TRIGGERED"
    assert HardSecurityRuleType.IDENTITY_MISMATCH.value == "IDENTITY_MISMATCH"
