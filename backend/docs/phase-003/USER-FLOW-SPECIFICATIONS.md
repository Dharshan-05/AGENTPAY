# AGENTPAY — User Flow Specifications

## 1. Overview

This document formalizes the detailed functional step-by-step flows for five canonical user journeys defined in Phase 001.

---

## 2. Detailed Functional User Flows

### Flow A: Agent Creation & Policy Configuration
```
[ USER ] ──> Clicks "Register Agent" ──> Fills Name & Purpose
   │
   ▼
[ SYSTEM ] ──> Generates Agent ID & 256-bit HMAC Secret ──> Displays Secret ONCE
   │
   ▼
[ USER ] ──> Opens AGENTGUARD Policy Configurator
   │       ──> Sets Max Single Limit (₹10,000)
   │       ──> Sets Auto-Approval Threshold (₹5,000)
   │       ──> Sets Allowed Categories (Electronics)
   ▼
[ SYSTEM ] ──> Persists Policy Rules ──> Initializes Redis Cache ──> Sets Agent State: ACTIVE
```

---

### Flow B: Safe Autonomous Purchase (Instant Auto-Approval)
```
[ AI AGENT ] ──> POST /api/v1/payment-intents (Amount: ₹2,500, Electronics, Signed HMAC)
   │
   ▼
[ GATEWAY ] ──> Verifies HMAC Signature & Nonce ──> PASS
   │
   ▼
[ AGENTGUARD ] ──> Evaluates 6-Stage Policy Pipeline
   │             ├── Amount (₹2,500 <= ₹10,000): PASS
   │             ├── Category (Electronics): ALLOWED
   │             └── Auto-Approval Ceiling (₹2,500 <= ₹5,000): ELIGIBLE
   ▼
[ FRAUDGUARD ] ──> Calculates 12 Features ──> RISK SCORE: 12/100 (LOW_RISK)
   │
   ▼
[ XAI ENGINE ] ──> Synthesizes Explanation: "Approved. Amount within auto-approval ceiling."
   │
   ▼
[ PAYMENT EXEC ] ──> Dispatches to Payment Adapter ──> Settlement SUCCESS
   │
   ▼
[ AUDIT LOG ] ──> Writes Append-Only Log with SHA-256 Block Hash ──> Live Dashboard Updates
```

---

### Flow C: High-Value Escalation & Human Approval
```
[ AI AGENT ] ──> POST /api/v1/payment-intents (Amount: ₹8,500, Electronics, Signed HMAC)
   │
   ▼
[ AGENTGUARD ] ──> Amount (₹8,500 > ₹5,000 Auto-Ceiling) ──> Decision: REVIEW
   │
   ▼
[ FRAUDGUARD ] ──> Anomaly Score: 45/100 ──> RISK SCORE: 52/100 (MEDIUM_RISK)
   │
   ▼
[ XAI ENGINE ] ──> Generates Trace: "Flagged for REVIEW. Exceeds auto-approval ceiling ₹5,000."
   │
   ▼
[ APPROVAL CTR ] ──> Sets State: PENDING_APPROVAL ──> Dispatches Push Alert to User Dashboard
   │
   ▼
[ USER ] ──> Inspects Approval Card & XAI Trace ──> Clicks "APPROVE"
   │
   ▼
[ PAYMENT EXEC ] ──> Resumes Pipeline ──> Executes Payment Adapter ──> Settlement SUCCESS
```

---

### Flow D: Severe Anomaly & Automatic Block
```
[ AI AGENT ] ──> POST /api/v1/payment-intents (Amount: ₹25,000, Gambling, Signed HMAC)
   │
   ▼
[ AGENTGUARD ] ──> Stage 3: Category Gambling BLOCKED ──> Stage 4: Amount Exceeds Limit
   │             └── Short-circuits ──> Decision: BLOCK
   ▼
[ FRAUDGUARD ] ──> Anomaly Score: 95/100 ──> RISK SCORE: 94/100 (CRITICAL_RISK)
   │
   ▼
[ SYSTEM ] ──> Terminates Execution ──> Dispatches Security Alert ──> Logs Audit Trace
```

---

### Flow E: Emergency Agent Revocation
```
[ USER ] ──> Clicks "EMERGENCY STOP" or "Revoke Agent"
   │
   ▼
[ SYSTEM ] ──> Updates Redis Edge Cache (user:emergency_stop = TRUE) in < 5ms
   │       ──> Updates Agent State to SUSPENDED / REVOKED
   │       ──> Purges Authentication Keys in < 10ms
   │       ──> Cancels Pending Intents in Queue
   ▼
[ AGENT REQUESTS ] ──> Reject with HTTP 403 ERR_EMERGENCY_STOP_ACTIVE / ERR_AGENT_REVOKED
```
