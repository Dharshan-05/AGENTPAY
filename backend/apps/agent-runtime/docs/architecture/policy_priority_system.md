# AGENTGUARD Architecture Specification: Phase 196 — Policy Priority System

## Overview
Phase 196 implements `PolicyPriorityService`, providing validation and deterministic sorting for policy priorities.

## Priority Bounds & Tie-Breaking
- **Priority Range**: `0 <= priority <= 10000` (integer, default 100). Higher numeric priority = stronger precedence.
- **Model Reuse**: Reuses `SecurityPolicy.priority` column in [`app/infrastructure/database/models/security_policy.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/security_policy.py). Zero duplicate schema fields.
- **Validation**: Out-of-bounds or negative priorities fail validation (`PRIORITY_BELOW_MINIMUM` / `PRIORITY_EXCEEDS_MAXIMUM`).
- **Sorting**: `sort_policies_by_priority(policies)` sorts by `priority DESC`, tie-breaking by `id ASC`.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
