# ATIM Group 9 — GitHub Architecture Research & Pattern Adaptation

## Executive Summary
This document analyzes industry standards in administrative policy control planes, Redis-backed rate limiting, enterprise quota management, and abuse prevention to inform **ATIM Group 9 (Phases 17 & 18)**.

In accordance with AGENTPAY core invariants:
- **LLM is an UNTRUSTED PROPOSAL ENGINE with ZERO FINANCIAL AUTHORITY**.
- **The LLM MUST NEVER participate in policy creation, approval, activation, quota setting, or rate-limit configuration**.
- **All governance policy mutations MUST enforce RBAC, Four-Eyes Separation of Duties (`creator != approver`), version immutability, and HMAC cryptographic signing**.

---

## Framework Analysis & Classification

| Framework | Primary Patterns & Architecture | AGENTPAY Adaptation Strategy | Classification | Justification & Security Boundaries |
|---|---|---|---|---|
| **HashiCorp Sentinel / OPA / NIST SP 800-53** | Policy lifecycle state machine (`DRAFT` $\rightarrow$ `APPROVED` $\rightarrow$ `ACTIVE`), version immutability (`v1`, `v2`), Four-Eyes control (`creator != approver`), RBAC authorization. | Implement `ATIMPolicyGovernanceService` managing policy lifecycle with strict state transitions, RBAC permissions, and `creator != approver` enforcement. | **ADAPT** | Adopt policy lifecycle & four-eyes control; REJECT allowing LLM or non-admin actors to mutate policies. |
| **Envoy / LiteLLM / Kong Rate Limiting** | Redis-backed sliding window rate limiting by `tenant_id`, `agent_id`, `endpoint`, return `HTTP 429` with `retry_after`. | Implement `ATIMRateLimiter` using atomic sliding window limiting backed by Redis / atomic memory primitives. | **ADAPT** | Adopt sliding window limiting; REJECT non-atomic GET/SET counter updates or client-chosen limit algorithms. |
| **Stripe / AWS Quotas & Abuse Prevention** | Quotas for requests/min, tokens/day, cost/day with `Decimal` precision; abuse escalation ladder (`THROTTLE`, `TEMPORARY_BLOCK`, `REQUIRE_HITL`, `PERMANENT_SECURITY_BLOCK`). | Implement `ATIMQuotaService` and `ATIMAbuseDetectionService` with `Decimal` quota limits and deterministic abuse escalation. | **ADAPT** | Adopt quota accounting & abuse escalation; REJECT floating-point math for quota thresholds or LLM self-overrides. |

---

## Detailed Pattern Decisions

### 1. Administrative Policy Control Plane (Phase 17)
- **ADAPT**: Strongly typed policy state transitions (`DRAFT` $\rightarrow$ `PENDING_APPROVAL` $\rightarrow$ `APPROVED` $\rightarrow$ `ACTIVE` $\rightarrow$ `SUSPENDED` $\rightarrow$ `RETIRED`). Enforce Four-Eyes principle (`creator != approver`) and SHA-256 HMAC cryptographic signing via `ATIMAuditLockService`.
- **REJECT**: Overwriting active policies or allowing LLM proposals to modify policy configuration.

### 2. Production API Hardening & Rate Limiting (Phase 18)
- **ADAPT**: Atomic sliding-window rate limiting before expensive LLM or database operations. Return HTTP 429 with safe structured JSON error response.
- **REJECT**: Exposing Redis internals, secret values, or provider credentials in HTTP 429 error payloads.

### 3. Enterprise Quota & Abuse Prevention (Phase 18)
- **ADAPT**: `Decimal` quota tracking for daily spend, token limits, and request volumes. Deterministic abuse escalation ladder (`THROTTLE` $\rightarrow$ `PERMANENT_SECURITY_BLOCK`).
- **REJECT**: Allowing floating-point math for financial quotas or letting clients override quota allocations.
