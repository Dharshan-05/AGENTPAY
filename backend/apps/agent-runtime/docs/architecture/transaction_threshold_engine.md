# AGENTGUARD Architecture Specification: Phase 191 — Transaction Threshold Engine

## Overview
Phase 191 implements `TransactionThresholdService`, providing decision-only evaluation of transaction-level spending thresholds (`minimum_amount`, `maximum_amount`, `approval_threshold`).

## Decision Pipeline & Financial Rules
- **Decision-Only Scope**: Does NOT execute payment transactions, deduct funds, or mutate ledger state.
- **Financial Precision**: All monetary values use Python `Decimal` exclusively. Floating-point arithmetic is strictly forbidden.
- **Currency Match Validation**: Compares `transaction.currency == threshold.currency`. Currency mismatch fails closed (`INVALID_CURRENCY`).
- **Threshold Outcomes**:
  - `amount < minimum_amount`: `DENIED` (`MINIMUM_THRESHOLD_BREACH`).
  - `amount > maximum_amount`: `DENIED` (`MAXIMUM_THRESHOLD_EXCEEDED`).
  - `amount > approval_threshold`: `REQUIRE_APPROVAL` (`APPROVAL_THRESHOLD_EXCEEDED`).
  - `amount <= approval_threshold`: `ALLOW` (`BELOW_THRESHOLD`).
- **Integration**: Integrated into `PolicyEvaluationService` in [`app/application/services/policy_evaluation_service.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/application/services/policy_evaluation_service.py).
