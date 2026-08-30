# AGENTPAY — Abuse Cases & Threat Modeling

## 1. Overview

This document specifies ten critical security abuse cases and threat vectors targeting autonomous agentic commerce. For each threat, explicit system detection mechanisms, decision outputs, user impact, and audit log requirements are established.

---

## 2. Abuse Case Specifications

### Abuse Case 1: Compromised AI Agent Attempts Unauthorized Payment
* **Threat**: A subverted or hacked AI AGENT attempts to transfer funds to an unauthorized external account.
* **Trigger**: Ingestion of a validly signed `PAYMENT INTENT` from an agent whose behavioral vector suddenly shifts.
* **Expected Detection**: FRAUDGUARD flags high behavioral anomaly vector distance and unverified target domain.
* **Expected Decision**: `BLOCK` (or `REVIEW` if amount is small but anomalous).
* **User Impact**: Payment prevented; user alerted to suspicious agent behavior.
* **Audit Requirement**: Complete trace logged with flag `ERR_BEHAVIORAL_ANOMALY`.

### Abuse Case 2: Agent Attempts Transaction Above Single Limit
* **Threat**: Agent logic requests ₹25,000 purchase when single limit is set to ₹10,000.
* **Trigger**: Intent payload `amount` exceeds configured single transaction ceiling.
* **Expected Detection**: AGENTGUARD single limit rule check evaluates to `FAIL`.
* **Expected Decision**: `BLOCK`.
* **User Impact**: Transaction rejected immediately before contacting payment gateway.
* **Audit Requirement**: Logged with reason code `ERR_SINGLE_LIMIT_EXCEEDED`.

### Abuse Case 3: Agent Attempts Restricted Category Transaction
* **Threat**: Agent attempts purchase at a gambling or digital casino merchant.
* **Trigger**: Intent payload `category` matches a forbidden MCC or blocked category list.
* **Expected Detection**: AGENTGUARD category check evaluates to `FAIL`.
* **Expected Decision**: `BLOCK`.
* **User Impact**: Intent terminated instantly; zero financial exposure.
* **Audit Requirement**: Logged with reason code `ERR_CATEGORY_BLOCKED`.

### Abuse Case 4: Rapid Velocity Flooding (Agent Infinite Loop)
* **Threat**: Software bug causes agent to submit 100 payment intents per second.
* **Trigger**: High request count (> 5 requests/sec) from single `Agent ID`.
* **Expected Detection**: Gateway rate limiter and FRAUDGUARD velocity counter flag rate spike.
* **Expected Decision**: `BLOCK` + Auto-suspend agent state.
* **User Impact**: Agent automatically paused to protect user bank balance.
* **Audit Requirement**: System alert generated; event logged as `ERR_VELOCITY_LIMIT_EXCEEDED`.

### Abuse Case 5: Sudden Behavioral Deviation (Anomaly Spike)
* **Threat**: Agent normally buying ₹500 office supplies suddenly requests ₹8,000 luxury items.
* **Trigger**: Intent amount is 4.5x standard deviations above historical agent mean.
* **Expected Detection**: FRAUDGUARD computes high $Z$-score and elevated `RISK SCORE` (78/100).
* **Expected Decision**: `REVIEW` (or `BLOCK` if cumulative limits breached).
* **User Impact**: Escalated to user Approval Center for manual visual confirmation.
* **Audit Requirement**: Decision trace logged with feature attribution showing amount anomaly spike.

### Abuse Case 6: Prompt Injection Exploit
* **Threat**: Malicious website content injects adversarial instructions into LLM prompt causing it to generate a payment request.
* **Trigger**: Agent submits intent payload containing untrusted prompt context.
* **Expected Detection**: AGENTGUARD evaluates policy caps independently of prompt contents; FraudGuard flags merchant domain mismatch.
* **Expected Decision**: `BLOCK` (Policy caps enforce hard ceiling regardless of LLM reasoning).
* **User Impact**: User funds remain safe despite LLM prompt compromise.
* **Audit Requirement**: Logged with rationale `ERR_POLICY_BOUNDARY_ENFORCED`.

### Abuse Case 7: Attacker Obtains Agent Secret Key
* **Threat**: Stolen HMAC secret key used by external attacker to forge agent requests.
* **Trigger**: Valid HMAC signature originating from unauthorized IP address / ASN.
* **Expected Detection**: FRAUDGUARD geo-mismatch flag + velocity anomaly; User triggers Emergency Stop.
* **Expected Decision**: `BLOCK` + Instant Credential Revocation.
* **User Impact**: User revokes key; all active caches purged in < 10ms.
* **Audit Requirement**: Key revocation logged in security event trail.

### Abuse Case 8: Replay Attack of Past Payment Request
* **Threat**: Attacker intercepts and replays a previous legitimate payment intent request payload.
* **Trigger**: Incoming request contains a previously seen `X-Agent-Nonce` or expired timestamp.
* **Expected Detection**: Gateway Nonce cache check evaluates to `DUPLICATE`.
* **Expected Decision**: `BLOCK` (HTTP 401 Unauthorized).
* **User Impact**: Replayed request rejected at the edge.
* **Audit Requirement**: Security alert logged as `ERR_REPLAY_ATTEMPT`.

### Abuse Case 9: Concurrent Duplicate Submission (Race Condition)
* **Threat**: Agent submits two identical intent payloads simultaneously to double-spend.
* **Trigger**: Identical `idempotency_key` received in parallel threads.
* **Expected Detection**: Redis distributed lock prevents parallel execution; second request receives cached response.
* **Expected Decision**: First request processed; second request returns cached status.
* **User Impact**: Exactly one payment executed; zero double-spending.
* **Audit Requirement**: Logged as `INFO_IDEMPOTENT_DUPLICATE_SERVED`.

### Abuse Case 10: Fraudulent Merchant Domain Spoofing
* **Threat**: Fake merchant domain created to impersonate legitimate store.
* **Trigger**: Intent `merchant_domain` has low domain age and low trust score (05/100).
* **Expected Detection**: FRAUDGUARD merchant trust score check returns severe risk penalty.
* **Expected Decision**: `BLOCK` (or `REVIEW` if amount is small).
* **User Impact**: Transaction halted; merchant flagged in global reputation database.
* **Audit Requirement**: Logged with reason code `ERR_MERCHANT_LOW_REPUTATION`.
