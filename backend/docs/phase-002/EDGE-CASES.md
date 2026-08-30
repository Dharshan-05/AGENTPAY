# AGENTPAY — Edge Cases & Fail-Safe Handling

## 1. Overview

This document specifies mandatory system behaviors and fail-safe handling rules for 20 technical edge cases across system boundaries, network failures, hardware timeouts, and data corruption scenarios.

---

## 2. Edge Case Specifications

| ID | Edge Case Scenario | System Handling & Fail-Safe Rule | Expected Response / Outcome |
| :--- | :--- | :--- | :--- |
| **EDG-001** | Expired Payment Intent | Intent age exceeds 15-minute TTL prior to approval. | Status set to `EXPIRED`; intent canceled automatically. |
| **EDG-002** | Invalid / Negative Amount | Payload `amount` is $\le 0$ or non-integer. | Schema validation fails; returns `400 Bad Request`. |
| **EDG-003** | Unsupported Currency | Currency code is not supported (e.g. non-INR for MVP).| Returns `400 Bad Request (ERR_UNSUPPORTED_CURRENCY)`. |
| **EDG-004** | Unknown Merchant Domain | Target merchant domain has zero historical rating. | FraudGuard assigns default conservative trust score (50/100). |
| **EDG-005** | Suspended Agent Request | Agent state is `SUSPENDED` due to Emergency Stop. | Edge gateway rejects request instantly (`403 Forbidden`). |
| **EDG-006** | Revoked Agent Credentials| Agent state is `REVOKED`. | Signature verification fails (`401 Unauthorized`). |
| **EDG-007** | Disabled User Account | Human owner account deactivated or locked. | Agent requests rejected (`403 Forbidden (ERR_USER_LOCKED)`). |
| **EDG-008** | Policy Rule Conflict | Overlapping whitelist and blacklist rules. | Restrictive rules ALWAYS take precedence (`BLOCK`). |
| **EDG-009** | Missing Risk Score | Risk calculation returns null or invalid format. | System defaults to `MEDIUM_RISK` and routes to `REVIEW`. |
| **EDG-010** | AI Model Unavailable | ML scoring container offline or timing out (> 100ms). | Falls back to deterministic rules; minimum `MEDIUM_RISK`. |
| **EDG-011** | XAI Service Failure | Natural language generator service unavailable. | Falls back to static template explanation string. |
| **EDG-012** | Payment Gateway Timeout | Gateway fails to respond within 5,000ms. | Intent marked `FAILED (ERR_GATEWAY_TIMEOUT)`; balance unlocked. |
| **EDG-013** | Network Disconnect mid-Execution | Socket drops during settlement call. | System executes reconciliation query against processor before retry.|
| **EDG-014** | Mismatched Idempotency Payload | Same `idempotency_key` submitted with different payload.| Returns `409 Conflict (ERR_IDEMPOTENCY_MISMATCH)`. |
| **EDG-015** | Parallel Daily Limit Race | Two concurrent transactions together exceed daily cap. | Database atomic row locks ensure second intent is `BLOCKED`. |
| **EDG-016** | Stale User Approval | User approves intent after it has transitioned to EXPIRED.| System rejects approval action (`422 Unprocessable Entity`). |
| **EDG-017** | Human Approval Timeout | User fails to act on `REVIEW` request within 15 mins. | Status transitions automatically to `REJECTED (ERR_TIMEOUT)`. |
| **EDG-018** | DB Pool Exhaustion | Relational DB connection pool full under surge load. | API returns `503 Service Unavailable` with `Retry-After: 5`. |
| **EDG-019** | Redis Cache Failure | Redis edge cache container crashes or unreachable. | System falls back to direct DB policy queries; latency degrades gracefully.|
| **EDG-020** | Partial Gateway Settlement | Processor returns pending/unclear settlement status. | Status set to `PROCESSING_UNKNOWN`; background worker reconciles. |
