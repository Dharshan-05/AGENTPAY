# AGENTGUARD Architecture Specification: Phase 189 — Spending Limit Engine

## Overview
Phase 189 implements `SpendingLimitService`, a dedicated spending-limit decision engine evaluating single transaction limits.

## Decision-Only Scope & Non-Side-Effect Guarantee
- **Read/Decision Only**: Does NOT execute transactions, deduct funds, reserve money, settle, or capture payments.
- **Financial Precision**: All monetary calculations use Python `Decimal` exclusively. Binary floating-point arithmetic is strictly forbidden.
- **Currency Validation**: Validates `request.currency == limit_currency`. Currency mismatch fails closed (`INVALID_CURRENCY`).
- **Boundaries**:
  - `projected_spending <= configured_limit`: `WITHIN_LIMIT`.
  - `projected_spending > configured_limit`: `LIMIT_EXCEEDED` (or `REQUIRES_APPROVAL` if enforcement mode is `warn`).
  - `amount <= 0`: `INVALID_AMOUNT`.
