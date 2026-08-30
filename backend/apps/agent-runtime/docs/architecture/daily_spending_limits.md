# AGENTGUARD Architecture Specification: Phase 190 — Daily Spending Limits

## Overview
Phase 190 implements `DailySpendingLimitService` and `DailySpendingUsageProvider`, enforcing cumulative daily spending limits on top of Phase 189.

## Architecture & Daily Window Semantics
- **Read/Decision Only**: Evaluates cumulative daily spending without executing payment transactions or mutating balances.
- **Deterministic Daily Window**: Uses UTC midnight-to-midnight (`00:00:00.000000` to `23:59:59.999999`) for accurate daily boundary evaluation.
- **Authoritative Database Usage**: `DailySpendingUsageProvider` queries sum of qualifying transactions in `PaymentOrder` within tenant and agent scope where `status IN ('completed', 'authorized', 'pending', 'created', 'paid')` and `currency_code == target_currency`.
- **Projected Usage**: `projected_usage = current_daily_usage + requested_amount`.
- **Decimal Precision**: Enforces `Decimal` financial arithmetic throughout usage provider and limit service.
