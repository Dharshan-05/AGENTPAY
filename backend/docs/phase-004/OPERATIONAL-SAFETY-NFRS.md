# AGENTPAY — Operational Safety Non-Functional Requirements

## 1. Overview

Operational Safety requirements define circuit breakers, dead-letter queues (DLQ) for un-processable intents, rate limiting safety caps, and Emergency Stop execution priority.

---

## 2. Requirement Baseline

### NFR-OPS-001: Dead-Letter Queue (DLQ) Isolation for Malformed Intents
* **NFR ID**: `NFR-OPS-001`
* **Title**: Automated Dead-Letter Queue (DLQ) Isolation & Alerting
* **Source FR**: `FR-ERR-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Operational Safety
* **Requirement**: Any intent payload that encounters repeated unhandled parsing exceptions or database lock deadlocks shall be moved to an isolated Dead-Letter Queue (DLQ) after 3 attempts, preventing poison-pill payloads from blocking event workers.
* **Rationale**: Isolates malformed payloads and guarantees pipeline execution flow.
* **Metric & Target**: Isolation after 3 retries; $100\%$ DLQ logging and alert dispatch.
* **Measurement Method**: Injecting corrupted intent payload into worker queue.
* **Acceptance Criteria**: Payload routed to DLQ table; operator security alert emitted.
* **Dependencies**: `FR-ERR-001`.
