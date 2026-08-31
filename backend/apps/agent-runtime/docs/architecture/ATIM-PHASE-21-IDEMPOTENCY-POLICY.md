# ATIM Phase 21 — Idempotency & Financial Consistency Policy

## 1. Non-Negotiable Financial Consistency Rules
1. **ZERO DOUBLE-PAYMENT GUARANTEE**: Retries, duplicate requests, worker restarts, or concurrent incoming submissions **MUST NEVER** execute the same financial transaction, payment, or settlement twice.
2. **PAYLOAD FINGERPRINT MATCHING**: Reusing an idempotency key with a altered payload **MUST** fail closed (`HTTP 400 Payload Mismatch`).
3. **SERVER-RESOLVED TENANT SCOPING**: Idempotency lookups are strictly scoped by server-resolved `current_user.tenant_id`. Cross-tenant idempotency key collisions are isolated and prevented.
4. **DECISION PRECEDENCE INTEGRITY**: Idempotency resolution **MUST NOT** override security blocks, AgentGuard denials, FraudGuard blocks, or HITL requirements.
