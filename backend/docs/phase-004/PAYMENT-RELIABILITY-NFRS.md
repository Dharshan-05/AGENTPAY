# AGENTPAY — Payment Reliability Non-Functional Requirements

## 1. Overview

Payment Reliability requirements establish gateway timeout SLAs, atomic state machine transition controls, and reconciliation logging standards.

---

## 2. Requirement Baseline

### NFR-PAY-001: Payment Gateway Hard Timeout SLA
* **NFR ID**: `NFR-PAY-001`
* **Title**: Hard 5,000ms Payment Gateway Settlement Timeout Limit
* **Source FR**: `FR-PAY-001`
* **Priority**: P0 | **Target Horizon**: MVP TARGET
* **Category**: Payment Reliability
* **Requirement**: The Payment Service adapter shall enforce a hard $5,000\text{ ms}$ timeout on settlement requests to external payment gateways (Razorpay / Simulator). If a gateway fails to respond within $5,000\text{ ms}$, the call is terminated and the intent transitions to `FAILED (ERR_GATEWAY_TIMEOUT)`.
* **Rationale**: Prevents hanging payment gateway connections from exhausting server thread pools and blocking user UI sessions.
* **Metric & Target**: Hard Timeout $\le 5,000\text{ ms}$; $100\%$ thread release.
* **Measurement Method**: Fault injection introducing 10-second latency on mock gateway endpoint.
* **Acceptance Criteria**: Payment adapter terminates connection at exactly 5,000ms and updates state to `FAILED`.
* **Dependencies**: `FR-PAY-001`.
