# Phase 147 — Plan Generation Architecture

## Purpose
Phase 147 implements deterministic plan generation (`PlanGenerationService`) for AGENTPAY, mapping normalized `StructuredIntent` into ordered `PlanStep` sequences.

## Planning Taxonomy Mapping
- `PAYMENT`: Validate intent $\rightarrow$ Lookup merchant $\rightarrow$ Check constraints $\rightarrow$ Request authorization $\rightarrow$ Prepare payment.
- `REFUND`: Validate intent $\rightarrow$ Lookup transaction $\rightarrow$ Verify eligibility $\rightarrow$ Prepare refund.
- `TRANSACTION_LOOKUP`: Validate intent $\rightarrow$ Query transaction records.
- `BALANCE_QUERY`: Validate intent $\rightarrow$ Query account balance.
- `MERCHANT_LOOKUP`: Validate intent $\rightarrow$ Query merchant catalog.
- `USER_LOOKUP`: Validate intent $\rightarrow$ Query user profile.
- `AGENT_OPERATION`: Validate intent $\rightarrow$ Inspect agent configuration.
- `UNKNOWN`: Reject unknown intent (`execution_eligible = False`).

## Invariants
- **100% Determinism**: `generate_plan(intent) == generate_plan(intent)`.
- **Decimal Precision**: Preserves exact `Decimal` representation.
- **Descriptive Flags**: `requires_authorization` and `requires_tool` are descriptive metadata flags only. NO execution or tool calling occurs.
