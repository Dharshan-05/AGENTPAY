# AGENTPAY — Product Pillars

## Pillar 1 — AGENT IDENTITY

In autonomous agentic commerce, anonymous or loosely authenticated execution is fundamentally unacceptable. Every AI AGENT operating within AGENTPAY must possess a verifiable identity anchored to a human owner and explicit cryptographic credentials.

### 1.1 Core Identity Attributes

| Attribute | Description | Example |
| :--- | :--- | :--- |
| **Agent ID** | Unique, immutable system UUID assigned upon registration. | `agt_8f9b2c3a-4e1d-4a5b` |
| **Agent Owner** | Foreign key link to the verified human user account. | `usr_71a04b12` |
| **Agent Purpose** | Human-readable functional description and scope. | `Personal Procurement Assistant` |
| **Agent Permissions** | Explicitly declared permission scopes granted by owner. | `[spend:limit_10k, cat:electronics]` |
| **Agent Capabilities** | Functional capabilities and supported payment channels. | `[intent_create, status_query]` |
| **Agent Status** | Current lifecycle state. | `ACTIVE`, `PAUSED`, `REVOKED`, `SUSPENDED` |
| **Agent Trust Level** | Composite score indicating historical reliability. | `HIGH_TRUST` (Score: 88/100) |
| **Agent Authentication**| HMAC key-pairs, RSA public keys, or OAuth2 client credentials. | `pk_live_agt_...` |
| **Agent Credentials** | Secure token material used for API request signing. | Encrypted API Secret Key |
| **Agent Lifecycle** | State transitions: `REGISTERED` -> `ACTIVE` -> `REVOKED`. | Timestamped lifecycle events |

---

## Pillar 2 — USER-CONTROLLED AUTHORIZATION

Human users retain complete control over autonomous AI AGENT spending at all times. Controls are preemptive, real-time, and fail-safe.

### 2.1 Governance Controls

* **Spending Limits**:
  * Per-transaction maximum amount (e.g., ₹10,000).
  * Daily aggregate spending limit (e.g., ₹25,000).
  * Monthly cumulative spending budget.
* **Merchant Restrictions**:
  * Whitelisted merchant domains / Merchant Identification Codes (MIDs).
  * Explicitly blocked merchant blacklists.
* **Category Restrictions**:
  * Category-level toggles (e.g., Allow `Electronics`, Block `Gambling` / `Adult` / `Crypto`).
* **Geographic & Location Restrictions**:
  * Permitted country/region codes (e.g., `IN` only).
  * IP range / geofencing boundaries.
* **Temporal Restrictions**:
  * Active operating windows (e.g., 09:00 AM - 09:00 PM IST).
  * Day-of-week operation toggles.
* **Approval Thresholds**:
  * Automatic approval ceiling (e.g., auto-approve transactions under ₹5,000 if compliant).
  * Mandatory human approval trigger (e.g., transactions above ₹5,000 require human confirmation).
* **Emergency Controls**:
  * **Emergency Stop ("Kill Switch")**: Instantly halts all active transactions across all agents for a user.
  * **Agent Revocation**: Immediately de-authenticates a specific AI AGENT, rendering its credentials invalid.

---

## Pillar 3 — AGENTGUARD (Policy Engine & Security Layer)

**AGENTGUARD** is the primary authorization and policy gatekeeper within AGENTPAY. Its sole mandate is answering the critical question:

> **"Is this AI AGENT permitted to perform this specific action under current user policies and context?"**

### 3.1 Policy Evaluation Flow

```
Payment Intent
     │
     ▼
Identity Check (Valid API Key / Signature?)
     │
     ├── NO ──> REJECT (401 Unauthorized)
     ▼ YES
Owner Status Check (Owner Account Active?)
     │
     ├── NO ──> REJECT (403 Forbidden)
     ▼ YES
Policy Rule Evaluation:
  ├── 1. Single Transaction Limit Check
  ├── 2. Daily / Monthly Cumulative Limit Check
  ├── 3. Category & Merchant Restriction Check
  ├── 4. Temporal & Geofencing Boundary Check
  └── 5. Agent Status & Velocity Check
     │
     ▼
AGENTGUARD Decision Output
```

### 3.2 Decision Outputs

AGENTGUARD outputs one of four deterministic decisions for every evaluated `PAYMENT INTENT`:

1. **ALLOW**: Transaction fully satisfies all user policy constraints and falls within autonomous approval limits. Proceeds directly to FRAUDGUARD risk scoring.
2. **REVIEW**: Transaction satisfies basic criteria but exceeds autonomous spending thresholds or exhibits minor boundary anomalies. Sent to the Approval Center for human confirmation.
3. **CHALLENGE**: Transaction encounters secondary validation requirements (e.g., requires 2FA or step-up authentication from the human owner).
4. **BLOCK**: Transaction explicitly violates one or more hard policy rules (e.g., forbidden merchant category, exceeded single transaction limit, revoked agent). Instantly terminated.
