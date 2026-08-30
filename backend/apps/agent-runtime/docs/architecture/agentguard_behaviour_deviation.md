# AGENTGUARD Architecture Specification: Phase 202 — Behaviour Deviation

## Overview
Phase 202 implements `BehaviourDeviationService`, evaluating deviations between proposed operations and historical baselines.

## Deviation Categories & Severity
- **Deviation Dimensions**: `AMOUNT_DEVIATION`, `MERCHANT_DEVIATION`, `CATEGORY_DEVIATION`, `CURRENCY_DEVIATION`.
- **Severity Hierarchy**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NORMAL`, `COLD_START`.
- **Advisory Signaling**: Behaviour deviation is advisory security signaling. High/critical deviation generates `REQUIRE_APPROVAL` advisory candidates in policy evaluation, but NEVER overrides an explicit `DENY`.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
