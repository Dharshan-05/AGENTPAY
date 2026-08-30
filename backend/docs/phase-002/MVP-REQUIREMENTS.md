# AGENTPAY — MVP Requirements Baseline

## 1. Overview

This document explicitly defines the subset of requirements required for the **AGENTPAY Hackathon MVP**. Every requirement listed here is classified as **P0 (Must Have)** and directly contributes to demonstrating the complete end-to-end user story defined in Phase 001.

---

## 2. Core MVP Execution Chain

The MVP must demonstrate this exact end-to-end execution path:

```
[ USER ]
  │ Creates Account & Registers AI AGENT
  │ Configures Spending Limits (Max ₹10,000; Auto-approve <= ₹5,000)
  ▼
[ AI AGENT ]
  │ Submits Signed PAYMENT INTENT (Amount, Merchant, Category)
  ▼
[ AGENTGUARD ]
  │ Evaluates HMAC Signature & Deterministic Policy Rules
  ▼
[ FRAUDGUARD ]
  │ Calculates 12 Anomaly Features & RISK SCORE (0 - 100)
  ▼
[ XAI ENGINE ]
  │ Ranks Top Risk Factors & Generates Natural Language Explanation
  ▼
[ AUTHORIZATION DECISION ]
  ├── ALLOW  ──> Auto-Executes via Payment Gateway Adapter (Razorpay Sandbox/Simulator)
  ├── REVIEW ──> Escalates to Approval Center UI ──> User Clicks "Approve" ──> Executes
  └── BLOCK  ──> Terminates Request ──> Generates Security Alert ──> Audit Logged
```

---

## 3. MVP Requirement Matrix

| Requirement ID | Domain | Short Title | MVP Scope Inclusion |
| :--- | :--- | :--- | :--- |
| `REQ-AUTH-001` | Auth | User Login & MFA | Password + JWT session management for user login. |
| `REQ-AUTH-002` | Auth | Agent HMAC Auth | HMAC-SHA256 signature verification on API headers. |
| `REQ-AUTH-003` | Auth | Timestamp Expiration | 300s timestamp expiration check. |
| `REQ-AUTH-004` | Auth | Replay Protection | Redis nonce caching for replay protection. |
| `REQ-AGENT-001`| Agent | Agent Registration | Web interface for enrolling agents and issuing credentials. |
| `REQ-AGENT-003`| Agent | Status Management | Pause/Resume/Revoke state toggles for agents. |
| `REQ-POLICY-001`| Policy | Single Transaction Limit | Enforcing per-transaction maximum limit (e.g. ₹10,000). |
| `REQ-POLICY-002`| Policy | Category Rules | Allowed (Electronics) vs Blocked (Gambling) category rules. |
| `REQ-POLICY-003`| Policy | Auto-Approval Ceiling | Threshold rule for auto-approve (₹5,000) vs human review. |
| `REQ-POLICY-004`| Policy | Emergency Stop | Global kill switch suspending all active user agents. |
| `REQ-PAY-001` | Payment | Payment Intent API | Ingesting structured intent JSON payload from agent. |
| `REQ-PAY-002` | Payment | Idempotency | 24-hour idempotency key duplicate prevention. |
| `REQ-PAY-003` | Payment | Gateway Adapters | Simulator + Razorpay API sandbox test mode adapters. |
| `REQ-FRAUD-001`| Fraud | Feature Extraction | Real-time calculation of 12 risk feature dimensions. |
| `REQ-FRAUD-002`| Fraud | Risk Scoring | Normalized `RISK SCORE` (0-100) and risk level assignment. |
| `REQ-XAI-001` | XAI | Feature Importance | Top 3 risk factor attribution weights. |
| `REQ-XAI-002` | XAI | Natural Language Summary| Human-readable plain text explanation synthesis. |
| `REQ-APP-001` | Approval| Real-time Alerting | Push alert to Approval Center for `REVIEW` intents. |
| `REQ-APP-002` | Approval| Human Decision | One-click Approve/Reject buttons updating payment state. |
| `REQ-AUD-001` | Audit | Immutable Log | Append-only logging of end-to-end decision traces. |

---

## 4. MVP Non-Requirements (Deferred Features)

Features deferred to Phase 2+ / Post-Hackathon to protect MVP delivery:
* Multi-currency forex conversion.
* Decentralized DID / Verifiable Credential agent identities.
* Automated scheduled key rotation with 24-hour overlap grace windows.
* Complex multi-tenant enterprise RBAC role management.
