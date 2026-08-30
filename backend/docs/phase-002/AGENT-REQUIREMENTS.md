# AGENTPAY — Agent Requirements

## 1. Overview

Agent requirements define the programmatic interfaces, authentication contracts, payload schemas, and operational constraints governing how **AI AGENT** entities interact with AGENTPAY.

---

## 2. Requirement Baseline

### 2.1 Agent Authentication & Header Requirements
* **REQ-AGT-001**: AI agents shall authenticate every HTTP request to AGENTPAY by providing required headers: `X-Agent-ID`, `X-Agent-Timestamp`, `X-Agent-Nonce`, and `X-Agent-Signature`.
* **REQ-AGT-002**: The `X-Agent-Signature` header shall be computed as an HMAC-SHA256 hash using the agent's assigned `secret_key` over the canonical request payload string:
  $$\text{Signature} = \text{HMAC-SHA256}(K_{\text{secret}}, \text{AgentID} \parallel \text{Timestamp} \parallel \text{Nonce} \parallel \text{Method} \parallel \text{Path} \parallel \text{BodyHash})$$
* **REQ-AGT-003**: Requests with timestamps older than 300 seconds (5 minutes) relative to server time shall be rejected with `401 Unauthorized (ERR_TIMESTAMP_EXPIRED)`.
* **REQ-AGT-004**: Requests containing a previously seen `X-Agent-Nonce` within a 15-minute window shall be rejected with `401 Unauthorized (ERR_REPLAY_ATTEMPT)`.

### 2.2 Payment Intent Creation
* **REQ-AGT-005**: AI agents shall initiate transactions by submitting a POST request to `/api/v1/payment-intents`.
* **REQ-AGT-006**: The intent request payload shall strictly adhere to the standardized JSON schema containing:
  * `idempotency_key`: Unique UUID v4 string.
  * `merchant_name`: String name of target merchant.
  * `merchant_domain`: Valid domain string.
  * `category`: Standard Merchant Category Code (MCC) or category string (e.g. "Electronics").
  * `amount`: Positive numerical value in minor currency units (e.g. 250000 for ₹2,500.00).
  * `currency`: ISO 4217 code (e.g. "INR").
  * `context_prompt`: (Optional) Natural language task context describing the purchase intent.
* **REQ-AGT-007**: The system shall validate all intent request payloads against JSON schema definitions prior to policy processing.

### 2.3 Idempotency & Duplicate Request Protection
* **REQ-AGT-008**: Every intent submission shall include a unique `idempotency_key` (UUID v4).
* **REQ-AGT-009**: If an agent submits a duplicate request with an identical `idempotency_key` within 24 hours, the system shall return the cached initial processing response with HTTP 200 OK without re-evaluating policies or executing payments.

### 2.4 Intent Status Polling & Webhook Callbacks
* **REQ-AGT-010**: AI agents shall be able to query transaction status by issuing a GET request to `/api/v1/payment-intents/{intent_id}`.
* **REQ-AGT-011**: The system shall support asynchronous webhook callbacks to agent endpoints when an intent state transitions to `AUTHORIZED`, `REJECTED`, or `EXECUTED`.

### 2.5 Rejection Feedback & Machine-Readable Reason Codes
* **REQ-AGT-012**: When an intent is rejected or blocked, the system response shall include a standardized `reason_code` (e.g., `ERR_LIMIT_EXCEEDED`, `ERR_CATEGORY_BLOCKED`, `ERR_HIGH_FRAUD_RISK`).
* **REQ-AGT-013**: Rejection responses shall provide machine-readable error metadata to allow the agent's logic engine to safely handle financial rejections without retrying illegal intents.

### 2.6 Credential Isolation Boundaries
* **REQ-AGT-014**: AI agents shall operate strictly via high-level `PAYMENT INTENT` tokens and shall NEVER have access to raw bank account credentials, credit card numbers, CVVs, or UPI PINs.
