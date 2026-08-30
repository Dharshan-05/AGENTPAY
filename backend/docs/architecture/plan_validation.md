# Phase 148 — Plan Validation Architecture

## Purpose
Phase 148 implements fail-closed plan validation (`PlanValidationService`) for AGENTPAY, validating `AgentPlan` objects before execution eligibility.

## Validation Checks
1. **Schema & Field Validity**: Non-empty steps, canonical step_id pattern (`^step-\d+$`).
2. **Step Uniqueness & Sequence**: Unique step_ids, contiguous sequence starting at 1.
3. **Dependency Integrity & DAG Verification**: Dependencies reference existing prior steps. Cycle detection via DFS ensures zero circular dependencies.
4. **Supported Action Taxonomy**: All actions must belong to canonical action set.
5. **Secret Leakage Detection**: Scans step inputs, descriptions, targets, and constraints for secret material. Fails validation if secrets detected and records a `malicious_plan_attempt` security event.
6. **UNKNOWN Intent Invariant**: If `intent_type == "UNKNOWN"`, plan MUST NOT have `execution_eligible = True`.
