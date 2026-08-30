# AGENTPAY — Acceptance Criteria Baseline

## 1. Overview

This document specifies concrete, testable Acceptance Criteria (AC) for every P0 requirement in AGENTPAY. Acceptance criteria are structured in standard **Given-When-Then** format to enable automated integration testing and validation.

---

## 2. Acceptance Criteria Baseline

### AC-AUTH-001 (User MFA Login)
* **Given**: A registered human user with MFA enabled.
* **When**: The user provides valid username, password, and correct 6-digit TOTP code.
* **Then**: The system issues a signed JWT access token (15m TTL) and redirects the user to the Web Dashboard.

### AC-AUTH-002 (Agent HMAC Signature Authentication)
* **Given**: An active AI AGENT with a registered secret key `K_secret`.
* **When**: The agent submits an API request with valid `X-Agent-Signature` calculated over canonical headers.
* **Then**: The system authenticates the request and proceeds to intent schema validation.

### AC-AUTH-003 (Timestamp Expiration Check)
* **Given**: An incoming agent API request.
* **When**: The `X-Agent-Timestamp` header differs by more than 300 seconds from server UTC time.
* **Then**: The system rejects the request with HTTP `401 Unauthorized` and reason code `ERR_TIMESTAMP_EXPIRED`.

### AC-AUTH-004 (Replay Nonce Protection)
* **Given**: An incoming agent API request.
* **When**: The `X-Agent-Nonce` string matches a nonce cached in Redis within the past 15 minutes.
* **Then**: The system rejects the request with HTTP `401 Unauthorized` and reason code `ERR_REPLAY_ATTEMPT`.

### AC-AGENT-001 (Agent Registration & Credential Generation)
* **Given**: An authenticated human user on the Agent Management page.
* **When**: The user submits agent registration details (Name: "Shopping Assistant", Purpose: "Procurement").
* **Then**: The system generates a unique `Agent ID` (UUID v4), displays a 256-bit HMAC secret key once, and stores the secret in Argon2id hashed form.

### AC-AGENT-003 (Agent Lifecycle State Transition)
* **Given**: An active AI AGENT with status `ACTIVE`.
* **When**: The human user clicks "Pause Agent" in the dashboard.
* **Then**: The system updates the agent DB status to `PAUSED`, purges Redis edge authentication cache in $< 10\text{ ms}$, and rejects subsequent agent API calls with HTTP `403 Forbidden`.

### AC-POLICY-001 (Single Transaction Limit Enforcement)
* **Given**: An agent with configured single transaction limit ₹10,000.
* **When**: The agent submits a `PAYMENT INTENT` with amount ₹25,000.
* **Then**: AGENTGUARD evaluates single limit check to `FAIL`, outputs decision `BLOCK`, and returns reason code `ERR_SINGLE_LIMIT_EXCEEDED`.

### AC-POLICY-002 (Category Restriction Enforcement)
* **Given**: An agent with blocked category "Gambling".
* **When**: The agent submits an intent for a merchant with MCC matching "Gambling".
* **Then**: AGENTGUARD outputs decision `BLOCK` with reason code `ERR_CATEGORY_BLOCKED`.

### AC-POLICY-003 (Auto-Approval Threshold Evaluation)
* **Given**: An agent with auto-approval limit ₹5,000 and max single limit ₹10,000.
* **When**: The agent submits a compliant intent for ₹2,500.
* **Then**: AGENTGUARD outputs decision `ALLOW` and forwards intent directly to payment execution.
* **When**: The agent submits a compliant intent for ₹8,500.
* **Then**: AGENTGUARD outputs decision `REVIEW` and dispatches an escalation alert to the Approval Center.

### AC-POLICY-004 (Emergency Stop Global Kill Switch)
* **Given**: Multiple active agents initiating transactions.
* **When**: The user clicks the "EMERGENCY STOP" button on the dashboard.
* **Then**: All user-owned agents transition to `SUSPENDED` in $< 100\text{ ms}$, pending intents are canceled, and subsequent API requests return `403 Forbidden`.

### AC-PAY-001 (Payment Intent Creation & Validation)
* **Given**: An authenticated active AI AGENT.
* **When**: The agent POSTs a well-formed JSON payload to `/api/v1/payment-intents`.
* **Then**: The system validates schema, assigns `intent_id`, and sets state to `CREATED`.

### AC-PAY-002 (Idempotency Protection)
* **Given**: A previously processed intent with `idempotency_key` = `KEY_123`.
* **When**: The agent submits a duplicate intent payload with `idempotency_key` = `KEY_123` within 24 hours.
* **Then**: The system returns the cached processing response (HTTP 200 OK) without re-evaluating policies or calling payment gateways.

### AC-FRAUD-001 (Feature Extraction & Risk Scoring)
* **Given**: A submitted payment intent payload.
* **When**: FRAUDGUARD processes the intent.
* **Then**: 12 risk features are calculated in $< 20\text{ ms}$, normalized into `RISK SCORE` (0-100), and assigned risk level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### AC-XAI-001 (Feature Importance & Natural Text Explanation)
* **Given**: A processed intent with computed risk score.
* **When**: The XAI engine executes.
* **Then**: The top 3 risk factors are ranked with weights, and a natural language summary sentence explaining the decision is attached to the output trace.

### AC-APP-001 (Human Approval Escalation & Execution)
* **Given**: A transaction in `PENDING_APPROVAL` status displayed in the Approval Center.
* **When**: The user inspects the XAI explanation trace and clicks "APPROVE".
* **Then**: The intent state updates to `AUTHORIZED`, executes payment settlement via the selected adapter, and notifies the agent.

### AC-AUD-001 (Immutable Audit Logging)
* **Given**: A completed transaction intent.
* **When**: The pipeline finishes execution (`EXECUTED`, `REJECTED`, or `BLOCKED`).
* **Then**: An end-to-end trace with SHA-256 block hash is logged to append-only audit tables.
