# AGENTGUARD Architecture Specification: Phase 198 — Intent Matching

## Overview
Phase 198 implements `IntentMatchingService`, evaluating signal matching across action, amount, currency, merchant, and category dimensions.

## Signal Weighting & Scoring
- **Signal Breakdown**:
  - Action Signal (Weight: `0.25`)
  - Amount Signal (Weight: `0.25`, Decimal precision)
  - Currency Signal (Weight: `0.20`, ISO uppercase)
  - Merchant Signal (Weight: `0.15`, UUID/slug)
  - Category Signal (Weight: `0.15`, Hierarchical support)
- **Critical Mismatch Cap**: If any critical financial dimension (`amount`, `currency`, or `action`) has status `MISMATCH`, `match_score` is capped at `Decimal("0.00")` and status is `MISMATCH`.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
