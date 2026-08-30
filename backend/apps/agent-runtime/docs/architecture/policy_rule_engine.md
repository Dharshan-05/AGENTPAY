# AGENTGUARD Architecture Specification: Phase 188 — Policy Rule Engine

## Overview
Phase 188 implements `PolicyRuleEngine`, establishing a type-safe, deterministic rule-evaluation layer beneath `PolicyEvaluationService`.

## Rule Architecture & Safety Invariants
- **Model Reuse**: Reuses existing `PolicyRule` ORM entity in [`app/infrastructure/database/models/policy_rule.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/policy_rule.py). Zero duplicate models created.
- **Rule Operators Registry (`RULE_OPERATOR_REGISTRY`)**:
  - Allowlisted operators: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `exists`, `not_exists`, `contains`, `not_contains`.
  - **Zero Dynamic Execution**: Zero `eval()`, `exec()`, or dynamic imports. Operator evaluation functions use pure Python comparison functions.
  - **Fail-Closed**: Unknown operators or runtime evaluation errors fail closed (`outcome = "ERROR"`, `reason_code = "UNKNOWN_OPERATOR"`).
- **Rule Ordering**: Rules are evaluated in deterministic priority order (`priority DESC, id ASC`).

## Evaluation Flow
```
PolicyEvaluationService
       ↓
PolicyRuleEngine.evaluate_rule()
       ↓
RULE_OPERATOR_REGISTRY (Allowlist)
       ↓
PolicyRuleResult (MATCH, NO_MATCH, DENY, REQUIRE_APPROVAL, ERROR)
```
