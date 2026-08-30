# AGENTPAY — MVP Scope

## 1. Hackathon MVP Objectives

The **AGENTPAY Hackathon MVP** is designed to demonstrate an end-to-end working implementation of autonomous agentic commerce authorization, risk evaluation, explainable decisioning, and payment orchestration.

The MVP focuses on demonstrating absolute reliability, architectural integrity, real-time XAI explainability, and human-in-the-loop safety within the constraints of a competitive hackathon timeline.

---

## 2. Minimum Successful Demo Flow

```
[ USER ]
  │ Registers Account & Enrolls AI AGENT
  │ Configures Spending Limits (e.g. Max ₹10,000; Auto-approve <= ₹5,000)
  ▼
[ AI AGENT ]
  │ Initiates PAYMENT INTENT (Amount, Merchant, Category)
  ▼
[ AGENTGUARD ]
  │ Validates Agent HMAC Signature & Evaluates Deterministic Policy Rules
  │ Output: Pass Policy / Check Approval Threshold
  ▼
[ FRAUDGUARD ]
  │ Calculates Anomaly Feature Map & Normalized RISK SCORE (0 - 100)
  │ Output: LOW / MEDIUM / HIGH / CRITICAL Risk
  ▼
[ XAI ENGINE ]
  │ Computes Feature Attribution & Generates Natural Language Explanation
  ▼
[ DECISION ENGINE ]
  ├── ALLOW  ──> Auto-Executes via Payment Gateway Adapter ──> Dashboard Update
  ├── REVIEW ──> Escalates to Approval Center ──> Human Approval ──> Execution
  └── BLOCK  ──> Terminates Request ──> Generates Security Alert ──> Audit Logged
```

---

## 3. MUST-HAVE Features for MVP

### 3.1 Authentication & Agent Registration
* User login and JWT session management.
* Registration of AI AGENT instances with unique `Agent ID` and HMAC Secret Key issuance.
* Agent lifecycle management (`ACTIVE`, `PAUSED`, `REVOKED`).

### 3.2 Policy Engine (AGENTGUARD)
* Rule definitions for:
  * Single-transaction spending limits.
  * Category-based allowed/blocked lists (e.g., Electronics allowed, Gambling blocked).
  * Auto-approval threshold limit (e.g., auto-approve under ₹5,000).
* Real-time policy evaluation returning deterministic status (`ALLOW`, `REVIEW`, `BLOCK`).

### 3.3 Risk & Fraud Engine (FRAUDGUARD)
* Real-time feature calculation:
  * Transaction amount delta against agent baseline.
  * Merchant domain trustworthiness score.
  * Category risk weighting.
  * Velocity / frequency anomaly detection.
* Combined statistical risk score generation (`RISK SCORE`: 0 - 100).

### 3.4 Explainable AI (XAI Engine)
* Feature importance ranking (identifying top 3 risk factors per transaction).
* Human-readable plain language explanation generation for every decision.
* Step-by-step decision trace generation stored with transaction record.

### 3.5 Payment Intent & Execution Abstraction
* Endpoint for submitting structured `PAYMENT INTENT` requests.
* Idempotency checking.
* Abstracted Payment Adapter (supporting simulated execution + Razorpay API test mode integration).

### 3.6 Human-in-the-Loop Approval Center
* Real-time user interface displaying transactions flagged for `REVIEW`.
* One-click "Approve" or "Reject" action buttons updating payment intent state.
* Emergency Stop ("Kill Switch") button instantly pausing all active agents.

### 3.7 Immutable Audit Trail & Dashboard UI
* Comprehensive audit trail viewing interface displaying historical decisions, risk scores, XAI rationales, and timestamps.
* Live Dashboard displaying agent status, policy enforcement statistics, and real-time transaction activity feed.

---

## 4. MVP Boundary & Architectural Trade-offs

| Domain | Hackathon MVP Realization | Production Vision Target |
| :--- | :--- | :--- |
| **Payment Settlement** | Abstracted Payment Gateway Adapter (Simulator + Razorpay Test Mode) | Direct Core Banking APIs, Automated UPI Clearing |
| **Fraud ML Models** | Hybrid Rule Engine + Lightweight ML Anomaly Classifier | Deep Ensemble Anomaly Models trained on massive fraud datasets |
| **Data Persistence** | PostgreSQL / SQLite with indexed audit log schemas | Distributed Ledger / HSM-backed Immutable Append-Only Ledger |
| **Identity Verification**| Cryptographic HMAC Key Pairs + JWT Auth | Hardware-Backed Secure Enclave Signatures / DID Standards |
