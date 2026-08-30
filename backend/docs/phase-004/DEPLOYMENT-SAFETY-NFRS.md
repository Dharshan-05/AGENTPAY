# AGENTPAY — Deployment Safety Non-Functional Requirements

## 1. Overview

Deployment Safety requirements define graceful container shutdown controls, inflight transaction drain procedures, database migration safety checks, and zero-downtime deployment rules.

---

## 2. Requirement Baseline

### NFR-DEP-001: Graceful Worker Shutdown & Inflight Intent Drain
* **NFR ID**: `NFR-DEP-001`
* **Title**: Graceful Worker Process Shutdown & 15-Second Inflight Intent Drain
* **Source FR**: `FR-PAY-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Deployment Safety
* **Requirement**: Upon receiving a SIGTERM signal during container redeployment, worker nodes shall cease accepting new HTTP connections and allow up to 15 seconds for active inflight payment intents to complete execution.
* **Rationale**: Prevents aborting payment settlement calls mid-flight during routine application updates.
* **Metric & Target**: Max 15-second drain window; $0$ aborted inflight payments.
* **Measurement Method**: Issuing `docker stop -t 15` during active intent load test.
* **Acceptance Criteria**: Inflight transactions complete normally; new requests route to ready replicas.
* **Dependencies**: None.
