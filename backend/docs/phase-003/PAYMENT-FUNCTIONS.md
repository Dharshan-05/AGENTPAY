# AGENTPAY — Payment Execution Functional Specifications

## 1. Overview

Payment Execution functions specify authorized intent routing, payment processor adapter dispatch (Simulator and Razorpay API Test Mode), settlement verification, and reconciliation logging.

---

## 2. Specifications

### FR-PAY-001: Authorized Intent Adapter Execution
* **FR ID**: `FR-PAY-001`
* **Title**: Authorized Intent Dispatch to Payment Processor Adapters
* **Source**: `REQ-PAY-003`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Payment Service (`SYSTEM`)
* **Goal**: Execute payment settlement for fully authorized intents via configured processor adapters.
* **Preconditions**: Payment intent state is `AUTHORIZED` with valid cryptographic signatures from AGENTGUARD and FRAUDGUARD.
* **Trigger**: Intent state transitions to `AUTHORIZED` (either via auto-approval or human approval action).
* **Inputs**: `intent_id` (string), `amount` (integer), `merchant_details` (object), `selected_adapter` (`SIMULATOR` / `RAZORPAY_SANDBOX`).
* **Main Flow**:
  1. Payment Service verifies `AUTHORIZED` state and digital authorization signature.
  2. Payment Service sets intent state to `PROCESSING`.
  3. Payment Service selects target adapter (`SIMULATOR` or `RAZORPAY_SANDBOX`).
  4. Payment Service invokes adapter settlement method: `adapter.executePayment(intentPayload)`.
  5. Adapter communicates with payment rail and returns settlement result (`SUCCESS` / `FAILURE`).
  6. Payment Service verifies settlement response:
     * If `SUCCESS`: State updated to `EXECUTED`; audit log recorded.
     * If `FAILURE`: State updated to `FAILED`; failure alert dispatched.
* **Alternative Flows**:
  * *AF-1 (Gateway Timeout)*: If adapter does not respond in 5,000ms, set state to `FAILED` with reason `ERR_GATEWAY_TIMEOUT`.
* **Business Rules**: `BR-001`, `BR-003`, `BR-004`.
* **State Changes**: Payment intent state transitions: `AUTHORIZED` $\rightarrow$ `PROCESSING` $\rightarrow$ `EXECUTED` (or `FAILED`).
* **Outputs**: Payment Settlement Receipt JSON object.
* **Error Conditions**: `ERR_GATEWAY_TIMEOUT`, `ERR_PAYMENT_REJECTED_BY_BANK`, `ERR_INVALID_AUTH_SIGNATURE`.
* **Security Requirements**: Direct payment calls without valid authorization signature are rejected by payment service adapter layer.
* **Audit Events**: `EVENT_PAYMENT_EXECUTED`, `EVENT_PAYMENT_FAILED`.
* **Acceptance Criteria**: `AC-PAY-001`, `AC-APP-001`.
* **Dependencies**: `FR-AGD-001`, `FR-RISK-001`, `FR-APP-002`.
