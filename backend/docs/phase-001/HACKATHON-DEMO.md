# AGENTPAY — Hackathon Demonstration Scenario

## 1. Demo Narrative & Setup

This document defines the canonical 3-minute live demonstration story for AGENTPAY, showcasing complete end-to-end agentic commerce governance, real-time risk assessment, XAI explainability, and human-in-the-loop escalation.

### User Baseline Configuration
* **User**: "Rahul Sharma" (Tech Lead)
* **Agent Registered**: "Personal Shopping Assistant AI" (`agt_shop_01`)
* **Policy Rules Configured in AGENTGUARD**:
  * Single Transaction Maximum Limit: **₹10,000**
  * Auto-Approval Threshold: **₹5,000** (Intents $\le$ ₹5,000 auto-approve if safe)
  * Allowed Category: **Electronics**
  * Blocked Category: **Gambling**

---

## 2. Live Demo Transaction Sequence

```
+-----------------------------------------------------------------------------------+
|                        LIVE DEMO TRANSACTIONS SEQUENCE                            |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  TRANSACTION A : ₹2,500  | Electronics  | Trusted Store     ==> [ ALLOW / AUTO ]  |
|  TRANSACTION B : ₹8,500  | Electronics  | Unknown Merchant  ==> [ REVIEW / HUMAN] |
|  TRANSACTION C : ₹25,000 | Gambling     | Suspicious Casino ==> [ BLOCK / ALERT ] |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### Transaction A: Compliant & Auto-Approved

```json
{
  "agent_id": "agt_shop_01",
  "merchant": "Trusted Electronics Store",
  "merchant_domain": "trusted-electronics.in",
  "category": "Electronics",
  "amount": 2500,
  "currency": "INR"
}
```

* **AGENTGUARD Evaluation**:
  * Amount check (₹2,500 $\le$ ₹10,000 limit): **PASS**
  * Category check ("Electronics"): **ALLOWED**
  * Auto-approval ceiling check (₹2,500 $\le$ ₹5,000 threshold): **ELIGIBLE**
* **FRAUDGUARD Evaluation**:
  * Anomaly Score: 10/100 | Merchant Trust: 95/100 | **RISK SCORE: 12/100 (LOW RISK)**
* **XAI Explanation Output**:
  > *"Transaction APPROVED. Amount ₹2,500 is within auto-approval threshold ₹5,000. Category 'Electronics' is explicitly allowed. Merchant trust rating is high (95/100)."*
* **Outcome**: **ALLOW** $\rightarrow$ Payment Executes Successfully $\rightarrow$ Live Dashboard updates.

---

### Transaction B: High-Value Escalation (Human-in-the-Loop)

```json
{
  "agent_id": "agt_shop_01",
  "merchant": "Unknown Electronics Distributor",
  "merchant_domain": "unknown-dist.net",
  "category": "Electronics",
  "amount": 8500,
  "currency": "INR"
}
```

* **AGENTGUARD Evaluation**:
  * Amount check (₹8,500 $\le$ ₹10,000 limit): **PASS**
  * Category check ("Electronics"): **ALLOWED**
  * Auto-approval ceiling check (₹8,500 > ₹5,000 threshold): **EXCEEDS AUTO-APPROVE**
* **FRAUDGUARD Evaluation**:
  * Anomaly Score: 45/100 | Merchant Trust: 50/100 | **RISK SCORE: 52/100 (MEDIUM RISK)**
* **XAI Explanation Output**:
  > *"Transaction flagged for HUMAN REVIEW. Amount ₹8,500 exceeds auto-approval threshold ₹5,000. Target merchant has neutral trust rating (50/100)."*
* **Outcome**: **REVIEW** $\rightarrow$ Escalated to Approval Center $\rightarrow$ User receives instant mobile push alert $\rightarrow$ User inspects XAI trace and clicks **"APPROVE"** $\rightarrow$ Payment Executes.

---

### Transaction C: Severe Anomaly & Automatic Block

```json
{
  "agent_id": "agt_shop_01",
  "merchant": "Unverified Digital Casino",
  "merchant_domain": "suspicious-casino-live.com",
  "category": "Gambling",
  "amount": 25000,
  "currency": "INR"
}
```

* **AGENTGUARD Evaluation**:
  * Amount check (₹25,000 > ₹10,000 limit): **FAIL (Exceeds Limit)**
  * Category check ("Gambling"): **FORBIDDEN / BLOCKED CATEGORY**
* **FRAUDGUARD Evaluation**:
  * Anomaly Score: 95/100 | Merchant Trust: 05/100 | **RISK SCORE: 94/100 (CRITICAL RISK)**
* **XAI Explanation Output**:
  > *"Transaction BLOCKED. Exceeds single transaction limit ₹10,000 by 150%. Category 'Gambling' is explicitly forbidden by user policy. Target merchant flagged for high fraud probability."*
* **Outcome**: **BLOCK** $\rightarrow$ Payment Terminated Immediately $\rightarrow$ Security Alert Generated $\rightarrow$ Immutable Audit Logged $\rightarrow$ Agent Flagged on Security Console.

---

## 3. Visual Presentation Flow for Judges

1. **Dashboard Overview**: Present active agents, live policy limits, and security posture.
2. **Trigger Transaction A**: Run agent script initiating ₹2,500 intent. Show immediate green "ALLOW" card, XAI text box, and execution checkmark.
3. **Trigger Transaction B**: Run agent script initiating ₹8,500 intent. Show real-time yellow "PENDING APPROVAL" card appearing on Approval Center. Judge sees mobile notification. Click "Approve", watch status turn green.
4. **Trigger Transaction C**: Run agent script initiating ₹25,000 malicious intent. Show immediate red "BLOCKED" alert card with detailed SHAP/XAI feature impact list explaining why payment was stopped.
5. **Audit Log Inspection**: Show complete immutable audit table recording all three transaction traces with full cryptographic hash proofs.
