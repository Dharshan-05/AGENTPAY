# AGENTPAY — 33: Database Index Strategy (Partial, Composite, Cover Indexes)

## 1. Primary Composite Index Matrix

* `idx_payment_intents_tenant_status`: `(tenant_id, status)` for tenant dashboard queries.
* `idx_idempotency_lookup`: `(tenant_id, operation, idempotency_key)` covering key verification.
* `idx_outbox_pending`: `(status, created_at) WHERE status = 'PENDING'` (Partial index for low-cost worker polling).
