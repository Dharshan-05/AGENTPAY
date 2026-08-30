# AGENTPAY — Payment Intent Functional Specifications

## 1. Overview

Payment Intent functions specify intent payload ingestion, schema validation, distributed idempotency lock management, cancellation workflows, and state query interfaces.

---

## 2. Specifications

### FR-INTENT-001: Payment Intent Payload Ingestion & Validation
* **FR ID**: `FR-INTENT-001`
* **Title**: Payment Intent Payload Ingestion & Schema Validation
* **Source**: `REQ-PAY-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: AI AGENT (`AI AGENT`)
* **Goal**: Ingest structured payment intent from an AI agent and initialize state.
* **Preconditions**: Request authenticated via `FR-AUTH-003`.
* **Trigger**: AI Agent POSTs payload to `/api/v1/payment-intents`.
* **Inputs**: `idempotency_key` (UUID v4), `merchant_name` (string), `merchant_domain` (string), `category` (string), `amount` (positive integer in minor units), `currency` ("INR"), `context_prompt` (optional string).
* **Main Flow**:
  1. System validates JSON payload against strict schema definitions.
  2. System checks `currency == "INR"` and `amount > 0`.
  3. System assigns `intent_id` (UUID v4 format: `intent_7f8a9b0c`).
  4. System acquires distributed idempotency lock (`FR-INTENT-002`).
  5. System records initial intent state: `CREATED`.
  6. System passes intent object to AGENTGUARD pipeline (`FR-AGD-001`).
* **Alternative Flows**:
  * *AF-1 (Schema Validation Error)*: Return HTTP 400 `ERR_INVALID_PAYLOAD_SCHEMA`.
  * *AF-2 (Invalid Currency)*: Return HTTP 400 `ERR_UNSUPPORTED_CURRENCY`.
* **Business Rules**: `BR-001`, `BR-008`.
* **Validation Rules**: `amount` must be integer $> 0$; `merchant_domain` must match domain regex.
* **State Changes**: Payment intent record created in `CREATED` state.
* **Outputs**: Payment Intent JSON response with `intent_id` and status `PROCESSING`.
* **Error Conditions**: `ERR_INVALID_PAYLOAD_SCHEMA`, `ERR_UNSUPPORTED_CURRENCY`, `ERR_INVALID_AMOUNT`.
* **Audit Events**: `EVENT_PAYMENT_INTENT_CREATED`.
* **Acceptance Criteria**: `AC-PAY-001`.
* **Dependencies**: `FR-AUTH-003`.

---

### FR-INTENT-002: Distributed Idempotency Lock Enforcement
* **FR ID**: `FR-INTENT-002`
* **Title**: Distributed Idempotency Lock Enforcement
* **Source**: `REQ-PAY-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: System (`SYSTEM`)
* **Goal**: Prevent duplicate transaction processing using Redis distributed locking.
* **Preconditions**: Payment intent contains valid `idempotency_key`.
* **Trigger**: Intent payload ingestion step.
* **Inputs**: `agent_id` (string), `idempotency_key` (UUID v4).
* **Main Flow**:
  1. System constructs lock key: `idempotency:<agent_id>:<idempotency_key>`.
  2. System attempts Redis lock acquisition using `SET key value NX PX 86400000` (24-hour TTL).
  3. If lock acquired, processing continues.
  4. Upon processing completion, system caches full HTTP response under lock key.
* **Alternative Flows**:
  * *AF-1 (Duplicate Idempotency Key)*: If lock key exists and cached response present, return cached response with HTTP 200 OK (`INFO_IDEMPOTENT_DUPLICATE_SERVED`).
  * *AF-2 (Payload Mismatch)*: If lock key exists but payload hash differs, return HTTP 409 `ERR_IDEMPOTENCY_MISMATCH`.
* **Business Rules**: `BR-008`.
* **Outputs**: Cached Response OR Lock Pass signal.
* **Audit Events**: `EVENT_IDEMPOTENT_DUPLICATE_SERVED`.
* **Acceptance Criteria**: `AC-PAY-002`.
* **Dependencies**: `FR-INTENT-001`.
