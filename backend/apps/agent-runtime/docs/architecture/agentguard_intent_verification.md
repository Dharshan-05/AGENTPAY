# AGENTGUARD Architecture Specification: Phase 197 — Intent Verification

## Overview
Phase 197 implements `IntentVerificationService`, establishing a deterministic intent verification subsystem prior to policy rule evaluation.

## Verification Pipeline & Fail-Closed Controls
- **Pipeline Order**:
  1. Identity & Tenant Verification (`AgentIdentityVerificationService`).
  2. Structure & Action Normalization (`pay`/`purchase` -> `PAYMENT`).
  3. Action, Currency, Amount, and Merchant Verification.
  4. Decision Generation (`VERIFIED`, `MISMATCH`, `INSUFFICIENT`, `INVALID`, `DENIED`).
- **Fail-Closed Semantics**: Missing declared intent returns `INSUFFICIENT` with `INTENT_MISSING` and halts policy evaluation.
- **Financial Precision**: Uses `Decimal` comparison for amounts and strict ISO string matching for currencies.
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
