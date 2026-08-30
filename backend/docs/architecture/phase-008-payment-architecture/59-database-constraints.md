# AGENTPAY — 59: Database Unique Constraints, Checks & Foreign Keys

## 1. Database Invariant Constraints

* **Unique Constraints**: `UNIQUE(tenant_id, idempotency_key)`, `UNIQUE(provider_payment_id)`, `UNIQUE(webhook_event_id)`.
* **Check Constraints**: `CHECK (amount > 0)`, `CHECK (refunded_amount <= original_amount)`.
* **Foreign Keys**: `ON DELETE RESTRICT` on all payment and order relationships to prevent accidental record purging.
