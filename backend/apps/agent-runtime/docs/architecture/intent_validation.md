# Phase 143 — Intent Validation Architecture

## Purpose
Phase 143 implements the Intent Validation layer (`IntentValidationService`) for AGENTPAY, validating `StructuredIntent` objects before normalization or storage.

## Validation Invariants
- **Fail-Closed & Deterministic**: Invalid payloads or unmapped intent types fail validation immediately.
- **Canonical Taxonomy Alignment**: Compatible with Phase 141 taxonomy (`PAYMENT`, `REFUND`, `TRANSACTION_LOOKUP`, `BALANCE_QUERY`, `MERCHANT_LOOKUP`, `USER_LOOKUP`, `AGENT_OPERATION`, `UNKNOWN`).
- **Confidence Bounding**: Scores must satisfy $0.00 \le \text{confidence} \le 1.00$.
- **Financial Precision**: Monetary amounts MUST use `Decimal` with positive non-zero bounds ($amount > 0.00$) and explicit ISO 4217 currency codes.
- **Representation vs Execution**: `UNKNOWN` intents remain valid representations but are marked `is_execution_eligible = False`.
- **Tenant & Lifecycle Scoping**: Verified against authenticated tenant and agent active lifecycle status (`AgentNotFoundError` / `IntentValidationError`).
