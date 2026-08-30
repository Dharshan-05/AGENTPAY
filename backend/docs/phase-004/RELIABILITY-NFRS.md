# AGENTPAY — Reliability Non-Functional Requirements

## 1. Overview

Reliability requirements define transaction execution guarantees, state machine integrity, double-spend prevention, retry controls, and failure recovery rules.

---

## 2. Requirement Baseline

### NFR-REL-001: Zero Double-Spend Guarantee
* **NFR ID**: `NFR-REL-001`
* **Title**: Absolute Zero Double-Spend Guarantee via Idempotency Locking
* **Source FR**: `FR-INTENT-002`, `BR-008`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Reliability / Payment Safety
* **Requirement**: The system shall guarantee $100.0\%$ prevention of double-spending or duplicate transaction execution under network retries, race conditions, or parallel agent requests.
* **Rationale**: In financial systems, a single duplicate payment execution causes immediate monetary loss and loss of trust.
* **Metric & Target**: $100.0\%$ Duplicate Prevention ($0$ duplicate executions allowed under any scenario).
* **Measurement Method**: Automated parallel load test submitting 1,000 concurrent duplicate requests with identical `idempotency_key` values.
* **Acceptance Criteria**: Exactly ONE transaction is executed; 999 requests return cached HTTP 200 responses.
* **Dependencies**: Redis distributed locking (`SETNX`).

---

### NFR-REL-002: Retry Limits & Exponential Backoff Control
* **NFR ID**: `NFR-REL-002`
* **Title**: Controlled Retries with Exponential Backoff & Jitter
* **Source FR**: `FR-PAY-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Reliability
* **Requirement**: Automatic retries against external payment processors shall be strictly capped at a maximum of 2 attempts using full jitter exponential backoff.
* **Rationale**: Aggressive un-throttled retries against payment rails risk cascading failures, rate-limit bans, and duplicate clearing attempts.
* **Metric & Target**: Max 2 retry attempts; initial backoff $500\text{ ms}$, multiplier $2.0 \times \text{jitter}$.
* **Measurement Method**: Network fault injection simulating transient HTTP 503 gateway responses.
* **Acceptance Criteria**: Processor calls stop after exactly 2 retries; intent state transitions to `FAILED`.
* **Dependencies**: `FR-PAY-001`.
