# AGENTPAY — Functional Acceptance Criteria Baseline

## 1. Overview

This document specifies concrete, testable Given-When-Then Acceptance Criteria for all P0 Functional Requirements in Phase 003.

---

## 2. Acceptance Criteria Specifications

### AC-FR-AUTH-001 (User Registration)
* **Given**: A guest user on the registration portal.
* **When**: The user submits email, password ($\ge 12$ chars), full name, and valid 6-digit TOTP verification code.
* **Then**: The system creates an `ACTIVE` user profile, hashes password via Argon2id, and returns signed JWT access tokens.

### AC-FR-AUTH-003 (Agent HMAC Authentication)
* **Given**: A registered active AI AGENT with secret key $K_{\text{secret}}$.
* **When**: The agent POSTs an intent request with valid `X-Agent-Signature` calculated over canonical request headers.
* **Then**: Gateway authenticates request and passes intent payload to AGENTGUARD pipeline.

### AC-FR-AUTH-004 (Timestamp Expiration Check)
* **Given**: An incoming agent request.
* **When**: `X-Agent-Timestamp` differs by $> 300\text{ seconds}$ from server UTC time.
* **Then**: Gateway rejects request with HTTP 401 `ERR_TIMESTAMP_EXPIRED`.

### AC-FR-AUTH-005 (Nonce Replay Check)
* **Given**: An incoming agent request.
* **When**: `X-Agent-Nonce` matches a nonce string cached in Redis within past 15 minutes.
* **Then**: Gateway rejects request with HTTP 401 `ERR_REPLAY_ATTEMPT`.

### AC-FR-AGENT-001 (Agent Enrolment)
* **Given**: An authenticated human account owner.
* **When**: The user submits agent name ("Procurement Bot") and purpose.
* **Then**: System generates UUID v4 `Agent ID`, displays 256-bit HMAC secret key once, and stores key hash in DB.

### AC-FR-AGENT-003 (Agent State Transition)
* **Given**: An active agent in `ACTIVE` state.
* **When**: User clicks "Pause Agent" in dashboard.
* **Then**: Agent state updates to `PAUSED`, Redis edge cache is updated in $< 10\text{ ms}$, and API calls return HTTP 403 `ERR_AGENT_PAUSED`.

### AC-FR-POLICY-001 (Single Limit Rule Check)
* **Given**: An agent with single transaction limit ₹10,000.
* **When**: Agent submits intent for ₹25,000.
* **Then**: AGENTGUARD Stage 4 check fails, decision outputs `BLOCK`, and reason code returns `ERR_SINGLE_LIMIT_EXCEEDED`.

### AC-FR-POLICY-002 (Category Restriction Check)
* **Given**: An agent with blocked category "Gambling".
* **When**: Agent submits intent for merchant category "Gambling".
* **Then**: AGENTGUARD Stage 3 check fails, decision outputs `BLOCK`, and reason code returns `ERR_CATEGORY_BLOCKED`.

### AC-FR-POLICY-003 (Auto-Approval Threshold Check)
* **Given**: An agent with auto-approval threshold ₹5,000.
* **When**: Agent submits compliant intent for ₹2,500.
* **Then**: Decision outputs `ALLOW` and intent executes automatically.
* **When**: Agent submits compliant intent for ₹8,500.
* **Then**: Decision outputs `REVIEW` and intent escalates to Approval Center.

### AC-FR-EMG-001 (Global Emergency Stop)
* **Given**: Multiple active agents submitting intents.
* **When**: User clicks "EMERGENCY STOP" button on dashboard.
* **Then**: All owned agents transition to `SUSPENDED` in $< 100\text{ ms}$, pending intents cancel, and subsequent API calls return HTTP 403 `ERR_EMERGENCY_STOP_ACTIVE`.

### AC-FR-INTENT-002 (Distributed Idempotency Lock)
* **Given**: A processed intent with `idempotency_key` = `KEY_999`.
* **When**: Agent submits duplicate intent payload with `idempotency_key` = `KEY_999` within 24 hours.
* **Then**: System returns cached HTTP response without re-evaluating policies or calling payment rails.

### AC-FR-PAY-001 (Authorized Payment Execution)
* **Given**: An intent in `AUTHORIZED` state.
* **When**: Payment Service receives authorized intent payload.
* **Then**: Payment Service invokes target adapter (Simulator or Razorpay Sandbox), executes settlement, updates state to `EXECUTED`, and logs append-only audit entry.
