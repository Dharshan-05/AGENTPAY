# Phase 141 — Intent Classification Architecture

## Purpose
Phase 141 introduces deterministic intent classification (`IntentClassificationService`) for AGENTPAY, mapping extracted semantic intents into a canonical taxonomy category.

## Canonical Taxonomy
- `PAYMENT`: Financial transfer or purchasing intent
- `REFUND`: Financial reimbursement or refund request
- `TRANSACTION_LOOKUP`: Ledger/transaction history query
- `BALANCE_QUERY`: Wallet/account balance check
- `MERCHANT_LOOKUP`: Merchant details query
- `USER_LOOKUP`: User profile/identity query
- `AGENT_OPERATION`: Agent status or lifecycle operation
- `UNKNOWN`: Ambiguous request or confidence < 0.50

## Architectural Invariants
- **Deterministic & Bounded**: Confidence scores are bounded ($0.00 \le \text{confidence} \le 1.00$). Low confidence (< 0.50) forces fallback to `UNKNOWN`.
- **Classification Only**: MUST NOT validate financial limits, execute payments, call tools, or mutate state.
