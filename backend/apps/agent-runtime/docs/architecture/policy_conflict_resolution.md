# AGENTGUARD Architecture Specification: Phase 195 — Policy Conflict Resolution

## Overview
Phase 195 implements `PolicyConflictResolutionService`, resolving competing decisions among applicable policies deterministically.

## Precedence & Resolution Rules
- **Core Decision Precedence**: `DENY` > `REQUIRE_APPROVAL` > `ALLOW`.
- **Precedence Hierarchy**:
  1. Decision Class (`DENY` [3] > `REQUIRE_APPROVAL` [2] > `ALLOW` [1]).
  2. Policy Priority (`priority DESC`).
  3. Specificity (`merchant` [3] > `category` [2] > `global` [1]).
  4. UUID tie-break (`str(policy_id) ASC`).
- **Structured Trace**: Returns winning policy UUID, winning rule UUID, conflicting policy UUIDs list, and resolution reason string.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
