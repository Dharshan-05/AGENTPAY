# AGENTPAY — Dashboard Functional Specifications

## 1. Overview

Dashboard functions specify data aggregation, real-time metric rendering, agent status cards, policy enforcement summaries, and transaction stream displays for human operators.

---

## 2. Specifications

### FR-DSH-001: Real-Time Dashboard Data Aggregation
* **FR ID**: `FR-DSH-001`
* **Title**: Real-Time Dashboard Metrics & Activity Feed Aggregation
* **Source**: `REQ-USR-020`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: Present real-time operational metrics, agent statuses, and transaction activity stream on the main web UI.
* **Preconditions**: User is authenticated.
* **Trigger**: User opens Web Dashboard home view.
* **Inputs**: Authenticated user session.
* **Main Flow**:
  1. System queries database and Redis cache for user's metrics:
     * **Total Active Agents**: Count of user agents in `ACTIVE` state.
     * **24h Spend Volume**: Aggregate INR spending total for past 24 hours.
     * **Policy Enforcement Stats**: Breakdown of `ALLOW`, `REVIEW`, and `BLOCK` counts.
     * **Pending Approvals**: Count of items in `PENDING_APPROVAL` status.
  2. System renders overview metrics cards and active agent summary cards.
  3. System connects to WebSocket feed for real-time live activity updates.
* **Outputs**: Dashboard Initial Data JSON payload.
* **Audit Events**: None (read query).
* **Acceptance Criteria**: `AC-USR-020`.
* **Dependencies**: `FR-AUTH-002`.
