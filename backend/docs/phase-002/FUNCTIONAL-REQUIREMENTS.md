# AGENTPAY — Comprehensive Functional Requirements Baseline

## 1. Requirement Inventory Overview

This document presents the complete functional requirements inventory for AGENTPAY. Every requirement is specified with a unique ID, title, description, primary actor, priority (`P0`: Must Have / MVP, `P1`: Should Have, `P2`: Future), acceptance criteria, dependencies, risk rating, and MVP classification.

---

## 2. Requirement Table

### Domain 1: Authentication & User Management

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-AUTH-001** | User MFA Login | User authenticates via password + TOTP/MFA token. | USER | P0 | User session issued upon valid MFA verification. | YES |
| **REQ-AUTH-002** | Agent HMAC Auth | Agent requests authenticated via HMAC-SHA256 signature. | AI AGENT | P0 | Valid signature authenticates agent request; invalid fails with 401. | YES |
| **REQ-AUTH-003** | Timestamp Window | Requests validated against 300s expiration window. | AI AGENT | P0 | Timestamps > 300s diff rejected with ERR_TIMESTAMP_EXPIRED. | YES |
| **REQ-AUTH-004** | Nonce Cache | Replay defense caching nonces in Redis for 15m. | AI AGENT | P0 | Duplicate nonce rejected with ERR_REPLAY_ATTEMPT. | YES |
| **REQ-USER-001** | User Profile Setup | User registers account and sets profile preferences. | USER | P0 | User profile stored with hashed credentials. | YES |

### Domain 2: Agent Management & Identity

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-AGENT-001**| Agent Enrolment | User creates new AI AGENT instance with purpose tag. | USER | P0 | Unique Agent ID and HMAC secret generated and stored. | YES |
| **REQ-AGENT-002**| Secret Display | System displays HMAC secret key exactly once. | USER | P0 | Secret key shown once; stored in hashed Argon2id format. | YES |
| **REQ-AGENT-003**| Agent Status Toggle| User pauses, resumes, or revokes agent lifecycle state.| USER | P0 | State transition updates database and purges Redis cache in < 10ms. | YES |
| **REQ-AGENT-004**| Key Rotation | Scheduled rotation of agent HMAC secret keys. | USER | P1 | Secondary key generated with 24-hour overlap window. | NO |

### Domain 3: AGENTGUARD Policy Engine

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-POLICY-001**| Limit Config | Configures per-transaction spending limit per agent. | USER | P0 | Single limit enforced; intent > limit rejected with ERR_LIMIT_EXCEEDED.| YES |
| **REQ-POLICY-002**| Category Restrictions| Configures allowed/blocked Merchant Category Codes. | USER | P0 | Intents for blocked MCC evaluate to BLOCK decision immediately. | YES |
| **REQ-POLICY-003**| Auto-Approve Limit| Configures spending ceiling for automatic approval. | USER | P0 | Compliant intents <= ceiling evaluate to ALLOW; > ceiling to REVIEW.| YES |
| **REQ-POLICY-004**| Emergency Stop | Global kill switch suspending all active agents. | USER | P0 | Hitting Emergency Stop halts all agents for user in < 100ms. | YES |

### Domain 4: Payment Intent & Processing

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-PAY-001** | Create Intent | Agent submits structured payment intent payload. | AI AGENT | P0 | Valid intent payload creates record in CREATED state. | YES |
| **REQ-PAY-002** | Idempotency Check | Prevents duplicate processing via idempotency_key. | AI AGENT | P0 | Duplicate key within 24h returns cached processing result. | YES |
| **REQ-PAY-003** | Gateway Adapter | Executes authorized payment via Simulator / Razorpay. | SYSTEM | P0 | Authorized intents dispatch to selected adapter for settlement. | YES |
| **REQ-PAY-004** | State Transitions | Enforces valid state machine execution pipeline. | SYSTEM | P0 | Invalid state jumps rejected; state log updated atomically. | YES |

### Domain 5: FRAUDGUARD Risk Engine

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-FRAUD-001**| Feature Extraction| Extracts 12 risk features (amount, velocity, MCC). | SYSTEM | P0 | Feature vector computed in < 20ms for every intent. | YES |
| **REQ-FRAUD-002**| Risk Scoring | Computes RISK SCORE (0-100) and fraud probability. | SYSTEM | P0 | Scores normalized and mapped to LOW/MEDIUM/HIGH/CRITICAL risk level.| YES |
| **REQ-FRAUD-003**| Fail-Safe Fallback| AI timeout falls back to deterministic rule scoring. | SYSTEM | P0 | AI failure sets min MEDIUM_RISK level; never auto-ALLOWs. | YES |

### Domain 6: XAI Explanation Engine

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-XAI-001** | Feature Importance| Ranks top 3 risk factors driving decision score. | SYSTEM | P0 | Decision trace contains top feature weights and risk push vectors. | YES |
| **REQ-XAI-002** | Natural Text Summary| Synthesizes decision into human-readable text. | SYSTEM | P0 | Plain language explanation generated and saved with decision record. | YES |

### Domain 7: Approval Center & Audit Trail

| Req ID | Title | Description | Actor | Priority | Acceptance Criteria | MVP |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-APP-001** | Real-time Alert | Dispatches alert for intents requiring human review. | USER | P0 | Alert pushed to dashboard/approval center within 500ms. | YES |
| **REQ-APP-002** | Human Action | User approves or rejects pending intent request. | USER | P0 | Approval transitions intent to AUTHORIZED; rejection to REJECTED. | YES |
| **REQ-AUD-001** | Immutable Audit | Writes end-to-end trace to append-only log table. | SYSTEM | P0 | Intent evaluation trace written with SHA-256 block hash. | YES |
