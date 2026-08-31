# ATIM Group 11 — GitHub Architecture Research & Pattern Adaptation

## Executive Summary
This document analyzes production patterns in distributed transaction consistency, Stripe-style idempotency APIs, transactional outbox messaging, and disaster recovery to inform **ATIM Group 11 (Phases 21 & 22)**.

In accordance with AGENTPAY core invariants:
- **LLM is an UNTRUSTED PROPOSAL ENGINE with ZERO FINANCIAL AUTHORITY**.
- **Idempotency, retries, worker crash recovery, and distributed locking MUST NEVER create a bypass around security boundaries or double-execute financial actions**.
- **Authoritative Decision Precedence MUST REMAIN**:
  `SECURITY BLOCK > PLAN INVALID > AGENTGUARD DENY > FRAUDGUARD BLOCK > QUOTA DENY > RATE LIMIT DENY > HITL REQUIRED > ALLOW`.

---

## Framework Analysis & Classification

| Framework | Primary Patterns & Architecture | AGENTPAY Adaptation Strategy | Classification | Justification & Security Boundaries |
|---|---|---|---|---|
| **Stripe Idempotency Engine** | Scoped idempotency keys `(tenant_id, agent_id, operation, key)`, request payload SHA-256 fingerprinting, deterministic execution state machine, returning saved result for duplicate keys. | Implement `ATIMIdempotencyService` with state machine (`RECEIVED`, `PROCESSING`, `AUTHORIZED`, `EXECUTING`, `SUCCEEDED`, `FAILED`, `DENIED`). | **ADAPT** | Adopt Stripe-style idempotency and payload hashing; REJECT globally un-scoped keys or allowing modified payloads with existing keys. |
| **Transactional Outbox Pattern** | Atomic database transactions storing outbox events alongside business state mutations, preventing dual-write inconsistencies. | Implement `ATIMTransactionalOutbox` ORM entity and recovery reconciler in `ATIMRecoveryService`. | **ADAPT** | Adopt outbox pattern for audit/compliance event consistency; REJECT non-transactional external side-effects. |
| **Resilience4j / Netflix Hystrix Crash Recovery** | Crash recovery worker reconciling stuck `PROCESSING` states after worker restarts; fail-closed behavior on database/Redis outages. | Implement `ATIMRecoveryService` for crash reconciliation and fail-closed dependency handling. | **ADAPT** | Adopt fail-closed crash reconciliation; REJECT recovering into `ALLOW` when authoritative security cannot be verified. |

---

## Detailed Pattern Decisions

### 1. Distributed State & Idempotency (Phase 21)
- **ADAPT**: Authoritative idempotency key scoping (`tenant_id + agent_id + operation + idempotency_key`). Enforce PostgreSQL UNIQUE constraints. Return existing authoritative execution result for identical duplicate requests.
- **REJECT**: Allowing client-supplied `tenant_id` to control idempotency scope, or allowing replayed requests with modified payloads.

### 2. Advanced Reliability & Recovery (Phase 22)
- **ADAPT**: Automatic crash recovery reconciling interrupted `PROCESSING` states after process restarts. Fail closed to `DENY / 503` if Redis or PostgreSQL dependencies become unavailable.
- **REJECT**: Retrying payment execution without provider-side idempotency or converting dependency failures into `ALLOW`.
