"""Deterministic Policy Rule Evaluation Engine for AGENTPAY (Phase 188)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.infrastructure.database.models.policy_rule import PolicyRule
from app.schemas.policy_rules import PolicyRuleContext, PolicyRuleResult

logger = logging.getLogger("agentguard.security.policy_rule_engine")

# Operator evaluation functions (Zero eval/exec, 100% type-safe Python logic)
OperatorFunc = Callable[[Any, Any], bool]


def _op_eq(actual: Any, target: Any) -> bool:
    if isinstance(actual, Decimal) or isinstance(target, Decimal):
        try:
            return Decimal(str(actual)) == Decimal(str(target))
        except Exception:
            return False
    return str(actual) == str(target)


def _op_neq(actual: Any, target: Any) -> bool:
    return not _op_eq(actual, target)


def _op_gt(actual: Any, target: Any) -> bool:
    if actual is None or target is None:
        return False
    try:
        return Decimal(str(actual)) > Decimal(str(target))
    except Exception:
        return False


def _op_gte(actual: Any, target: Any) -> bool:
    if actual is None or target is None:
        return False
    try:
        return Decimal(str(actual)) >= Decimal(str(target))
    except Exception:
        return False


def _op_lt(actual: Any, target: Any) -> bool:
    if actual is None or target is None:
        return False
    try:
        return Decimal(str(actual)) < Decimal(str(target))
    except Exception:
        return False


def _op_lte(actual: Any, target: Any) -> bool:
    if actual is None or target is None:
        return False
    try:
        return Decimal(str(actual)) <= Decimal(str(target))
    except Exception:
        return False


def _op_in(actual: Any, target: Any) -> bool:
    if actual is None or target is None:
        return False
    if isinstance(target, (list, set, tuple)):
        return str(actual) in [str(x) for x in target]
    return str(actual) in str(target)


def _op_not_in(actual: Any, target: Any) -> bool:
    return not _op_in(actual, target)


def _op_exists(actual: Any, target: Any) -> bool:
    return actual is not None


def _op_not_exists(actual: Any, target: Any) -> bool:
    return actual is None


def _op_contains(actual: Any, target: Any) -> bool:
    if actual is None or target is None:
        return False
    return str(target).lower() in str(actual).lower()


def _op_not_contains(actual: Any, target: Any) -> bool:
    return not _op_contains(actual, target)


RULE_OPERATOR_REGISTRY: dict[str, OperatorFunc] = {
    "eq": _op_eq,
    "equals": _op_eq,
    "neq": _op_neq,
    "not_equals": _op_neq,
    "gt": _op_gt,
    "greater_than": _op_gt,
    "gte": _op_gte,
    "greater_than_or_equal": _op_gte,
    "lt": _op_lt,
    "less_than": _op_lt,
    "lte": _op_lte,
    "less_than_or_equal": _op_lte,
    "in": _op_in,
    "not_in": _op_not_in,
    "exists": _op_exists,
    "not_exists": _op_not_exists,
    "contains": _op_contains,
    "not_contains": _op_not_contains,
}


class PolicyRuleEngine:
    """Production Rule Evaluation Engine executing security policy rules (Phase 188)."""

    def evaluate_rule(self, rule: PolicyRule, context: PolicyRuleContext) -> PolicyRuleResult:
        """Evaluate a single PolicyRule against PolicyRuleContext fail-closed (Phase 188)."""
        now = datetime.now(UTC)

        # 1. Rule status & lifecycle validation
        if rule.status != "active" or rule.deleted_at is not None:
            return PolicyRuleResult(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                outcome="NO_MATCH",
                reason_code="RULE_INACTIVE",
                explanation=f"Rule '{rule.name}' is inactive or archived.",
                evaluated_at=now,
            )

        # 2. Window boundary check
        if (rule.starts_at and rule.starts_at > now) or (rule.ends_at and rule.ends_at < now):
            return PolicyRuleResult(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                outcome="NO_MATCH",
                reason_code="RULE_OUT_OF_WINDOW",
                explanation=f"Rule '{rule.name}' is outside effective time window.",
                evaluated_at=now,
            )

        # 3. Lookup field & operator
        op_name = rule.operator.lower()
        if op_name not in RULE_OPERATOR_REGISTRY:
            logger.warning("Unknown rule operator '%s' for rule ID %s", rule.operator, rule.id)
            return PolicyRuleResult(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                outcome="ERROR",
                reason_code="UNKNOWN_OPERATOR",
                explanation=f"Unknown rule operator '{rule.operator}'.",
                evaluated_at=now,
            )

        field_name = rule.condition_payload.get("field", "amount")
        target_value = rule.condition_payload.get("value")

        actual_value = getattr(context, field_name, None)
        if actual_value is None and isinstance(context.metadata, dict):
            actual_value = context.metadata.get(field_name)

        op_func = RULE_OPERATOR_REGISTRY[op_name]

        try:
            matched = op_func(actual_value, target_value)
        except Exception as exc:
            logger.error("Error evaluating rule %s: %s", rule.id, exc)
            return PolicyRuleResult(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                outcome="ERROR",
                reason_code="RULE_EVALUATION_ERROR",
                explanation=f"Rule evaluation encountered error: {exc}",
                evaluated_at=now,
            )

        if not matched:
            return PolicyRuleResult(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                outcome="NO_MATCH",
                reason_code="RULE_CONDITION_UNMET",
                explanation=f"Rule condition '{field_name} {op_name} {target_value}' unmet.",
                evaluated_at=now,
            )

        # 4. Map rule action to result outcome
        action = rule.action.lower()
        outcome = "MATCH"
        if action in ("deny", "block"):
            outcome = "DENY"
        elif action in ("require_approval", "challenge", "review"):
            outcome = "REQUIRE_APPROVAL"

        return PolicyRuleResult(
            rule_id=rule.id,
            rule_type=rule.rule_type,
            outcome=outcome,
            reason_code=f"RULE_MATCH_{rule.slug.upper()}",
            explanation=f"Rule '{rule.name}' matched with action '{action}'.",
            evaluated_at=now,
            metadata={"field": field_name, "action": action},
        )
