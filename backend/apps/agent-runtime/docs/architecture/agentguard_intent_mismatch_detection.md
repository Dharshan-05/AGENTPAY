# AGENTGUARD Architecture Specification: Phase 199 — Intent Mismatch Detection

## Overview
Phase 199 implements `IntentMismatchDetectionService`, classifying intent deviations into structured severity levels.

## Severity Taxonomy & Decision Controls
- **Taxonomy**: `AMOUNT_MISMATCH`, `CURRENCY_MISMATCH`, `MERCHANT_MISMATCH`, `ACTION_MISMATCH`, `CATEGORY_MISMATCH`, `PRODUCT_MISMATCH`, `QUANTITY_MISMATCH`.
- **Severity Classification**:
  - `CRITICAL`: Amount, Currency, Merchant mismatches.
  - `HIGH`: Action, Product mismatches.
  - `MEDIUM`: Category, Quantity mismatches.
  - `NONE`: Zero mismatches.
- **Fail-Closed Execution Gate**: Any `CRITICAL` or `HIGH` severity mismatch sets `can_proceed = False`, forcing policy evaluation to return `DENIED`.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
