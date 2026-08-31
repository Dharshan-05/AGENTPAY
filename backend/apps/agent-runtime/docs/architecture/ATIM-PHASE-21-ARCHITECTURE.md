# ATIM Phase 21 Architecture — Distributed State, Idempotency & Transaction Consistency

## Executive Summary
**ATIM Phase 21** implements a Stripe-grade distributed idempotency and transactional consistency engine for **AgentPay Transaction Intelligence Model (ATIM)**.

Phase 21 features:
1. **Authoritative Idempotency Key Scoping**: Scoped by `(tenant_id, agent_id, operation, idempotency_key)` using server-resolved `tenant_id`. Client-supplied or LLM-generated tenant IDs are explicitly ignored.
2. **Canonical Payload Fingerprinting**: Computes SHA-256 canonical hash over request payload. Reusing an idempotency key with a materially different payload is immediately rejected (`HTTP 400 Bad Request`).
3. **Deterministic Idempotency State Machine (`IdempotencyState`)**:
   `RECEIVED` $\rightarrow$ `PROCESSING` $\rightarrow$ `AUTHORIZED` $\rightarrow$ `EXECUTING` $\rightarrow$ `SUCCEEDED` / `FAILED` / `DENIED`.
4. **Concurrent Request De-duplication**: Concurrent identical requests resolve atomically. The first request proceeds; subsequent requests wait for or return the existing authoritative execution response.
5. **Zero Double-Execution Contract**: Guaranteed single execution for financial transactions, payment authorization, and settlement actions.

---

## Idempotency Lifecycle & Concurrent Execution Flow

```text
INCOMING REQUEST (Tenant T1, Key K1)
                 │
                 ▼
 CANONICAL PAYLOAD SHA-256 FINGERPRINT
                 │
                 ▼
   IDEMPOTENCY LOOKUP (T1 + A1 + Op + K1)
                 │
  ├── Duplicate Key + Matches Payload + Status=SUCCEEDED ──► Return Saved Result
  ├── Duplicate Key + Mismatched Payload ──────────────────► REJECT (HTTP 400 Payload Mismatch)
  ├── Duplicate Key + Status=PROCESSING ────────────────────► REJECT (HTTP 409 In Progress)
  └── First Time Key ───────────────────────────────────────► Create Record (Status=PROCESSING)
                 │
                 ▼
     ATIM PIPELINE EXECUTION
                 │
                 ▼
  UPDATE RECORD (Status=SUCCEEDED/DENIED, Save Response)
```
