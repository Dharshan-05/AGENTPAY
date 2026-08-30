# AGENTPAY — Resilience Non-Functional Requirements

## 1. Overview

Resilience requirements define fault handling, component failure modes, degraded operational modes, circuit breakers, and fail-safe security defaults under hardware or network outages.

---

## 2. Requirement Baseline

### NFR-RESL-001: Fail-Safe Security Default on Internal Outages
* **NFR ID**: `NFR-RESL-001`
* **Title**: Non-Negotiable Fail-Safe Security Default on Internal Faults
* **Source FR**: `FR-ERR-001`, `BR-012`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Resilience / Security
* **Requirement**: If any internal service (Database, Redis, FRAUDGUARD AI container, or XAI Engine) experiences a crash, timeout, or uncaught exception, the system shall default the decision to `BLOCK` (or `REVIEW` for human inspection). The system shall NEVER automatically default to `ALLOW`.
* **Rationale**: In FinTech security, partial failure must default to maximum safety to protect user funds.
* **Metric & Target**: $100.0\%$ Fail-Safe Compliance ($0$ unverified `ALLOW` decisions under any fault scenario).
* **Measurement Method**: Fault injection suite throwing runtime exceptions across all pipeline stages.
* **Acceptance Criteria**: All fault-injected requests return HTTP 500 error payload or output decision `BLOCK` / `REVIEW`. Zero requests evaluate to `ALLOW`.
* **Dependencies**: `FR-ERR-001`.

---

### NFR-RESL-002: Circuit Breaker Protection on Payment Gateways
* **NFR ID**: `NFR-RESL-002`
* **Title**: Gateway Circuit Breaker Pattern & Fallback Isolation
* **Source FR**: `FR-PAY-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Resilience
* **Requirement**: The Payment Service shall implement a Circuit Breaker pattern on external gateway endpoints. If 5 consecutive settlement calls fail or time out within 60s, the circuit breaker opens for 30s.
* **Rationale**: Prevents thread pool exhaustion and cascading system failure when a payment rail experiences a major outage.
* **Metric & Target**: Circuit opens after 5 failures in 60s; reset timeout 30s; fallback return `ERR_GATEWAY_CIRCUIT_OPEN`.
* **Measurement Method**: Mock adapter failure injection.
* **Acceptance Criteria**: Circuit breaker opens on 5th failure; subsequent calls immediately fail fast with `ERR_GATEWAY_CIRCUIT_OPEN`.
* **Dependencies**: `FR-PAY-001`.
