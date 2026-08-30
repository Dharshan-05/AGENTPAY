# AGENTPAY — Human Approval Center Functional Specifications

## 1. Overview

Human Approval Center functions specify real-time escalation queue management, UI card rendering, user approve/reject single-click actions, and automatic 15-minute timeout rejections.

---

## 2. Specifications

### FR-APP-001: Real-time Review Escalation Alerting & Queue Ingestion
* **FR ID**: `FR-APP-001`
* **Title**: Real-time Review Escalation Queue Ingestion & Alert Dispatch
* **Source**: `REQ-APP-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human Approval System (`SYSTEM`)
* **Goal**: Ingest intents with decision `REVIEW` into the real-time approval queue and dispatch push notifications.
* **Preconditions**: Decision Engine outputs decision `REVIEW`.
* **Trigger**: Transaction state transitions to `PENDING_APPROVAL`.
* **Inputs**: `intent_id`, `agent_id`, `amount`, `merchant`, `risk_score`, `xai_explanation`.
* **Main Flow**:
  1. System sets intent state to `PENDING_APPROVAL` with expiration timestamp ($T_{\text{now}} + 15\text{ minutes}$).
  2. System adds intent record to user's real-time Approval Center queue.
  3. System dispatches WebSocket push event to active Web Dashboard clients.
  4. System renders interactive approval card displaying amount, merchant, `RISK SCORE`, top risk factors, and XAI natural language summary.
* **Outputs**: Real-Time Approval Queue Event object.
* **Audit Events**: `EVENT_APPROVAL_REQUESTED`.
* **Acceptance Criteria**: `AC-APP-001`.
* **Dependencies**: `FR-RISK-001`, `FR-XAI-002`.

---

### FR-APP-002: Human Single-Click Approve/Reject Action Workflow
* **FR ID**: `FR-APP-002`
* **Title**: Human Single-Click Approval Action & Pipeline Resumption
* **Source**: `REQ-APP-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: Process human user approval or rejection action on a pending transaction.
* **Preconditions**: Intent exists in `PENDING_APPROVAL` state; user session authenticated.
* **Trigger**: User clicks "APPROVE" or "REJECT" button on Approval Card.
* **Inputs**: `intent_id` (string), `action` (`APPROVE` / `REJECT`), `user_id` (string).
* **Main Flow**:
  1. System verifies active user JWT session matches intent `owner_id`.
  2. System acquires atomic lock on `intent_id` to prevent duplicate action processing.
  3. If action == `APPROVE`:
     * State updated to `AUTHORIZED`.
     * Payment Service executes settlement adapter (`FR-PAY-001`).
  4. If action == `REJECT`:
     * State updated to `REJECTED`.
     * Agent notified of rejection (`ERR_HUMAN_REJECTED`).
  5. Approval card removed from active UI queue.
* **Alternative Flows**:
  * *AF-1 (Intent Expired)*: If intent timestamp > 15m, reject action with HTTP 422 `ERR_APPROVAL_EXPIRED`.
* **Business Rules**: `BR-001`, `BR-006`.
* **Outputs**: Intent Execution Status (`AUTHORIZED` / `REJECTED`).
* **Audit Events**: `EVENT_APPROVAL_GRANTED`, `EVENT_APPROVAL_REJECTED`.
* **Acceptance Criteria**: `AC-APP-001`.
* **Dependencies**: `FR-APP-001`, `FR-PAY-001`.
