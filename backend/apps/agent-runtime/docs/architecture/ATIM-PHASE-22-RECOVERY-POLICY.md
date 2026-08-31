# ATIM Phase 22 — Recovery & Disaster Resilience Policy

## 1. Core Recovery & Resilience Rules
1. **FAIL-CLOSED RECOVERY**: Interrupted execution recovery **MUST NEVER** default to `ALLOW`. Unverifiable or ambiguous external states default to `DENY` or `HTTP 503`.
2. **TRANSACTIONAL OUTBOX CONSISTENCY**: Compliance audit events **MUST** be written to the `atim_transactional_outbox` table in the same PostgreSQL transaction as the state transition.
3. **NO AMBIGUOUS PAYMENT RETRIES**: If a payment provider call times out after request transmission, the system **MUST NOT** blindly retry without verifying provider-side status or idempotency.
4. **DEPENDENCY FAIL-CLOSED INTEGRITY**: Loss of Redis, PostgreSQL, or Audit Service connectivity **MUST** halt financial execution (`HTTP 503 Service Unavailable`).
