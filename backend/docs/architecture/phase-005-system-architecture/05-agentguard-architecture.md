# AGENTPAY — 05: AGENTGUARD Security Control Plane Architecture

## 1. Architectural Independence & Mandate

**AGENTGUARD** acts as an architecturally independent security control plane operating between AI AGENT logic and payment execution rails. Even if an AI agent's internal LLM planner decides to proceed with a purchase intent, AGENTGUARD possesses complete deterministic authority to override, challenge, or block the transaction.

---

## 2. AGENTGUARD Precedence Evaluation Flow

```mermaid
graph TD
    INTENT[Incoming Payment Intent Request] --> S1{Stage 1: Emergency Stop Active?}
    S1 -- YES --> BLOCK1[BLOCK: ERR_EMERGENCY_STOP_ACTIVE]
    S1 -- NO --> S2{Stage 2: Agent Status == ACTIVE?}
    S2 -- NO --> BLOCK2[BLOCK: ERR_AGENT_NOT_ACTIVE]
    S2 -- YES --> S3{Stage 3: Category in Blacklist?}
    S3 -- YES --> BLOCK3[BLOCK: ERR_CATEGORY_BLOCKED]
    S3 -- NO --> S4{Stage 4: Amount <= Single Limit?}
    S4 -- NO --> BLOCK4[BLOCK: ERR_SINGLE_LIMIT_EXCEEDED]
    S4 -- YES --> S5{Stage 5: Cumulative Amount <= Budget?}
    S5 -- NO --> BLOCK5[BLOCK: ERR_DAILY_BUDGET_EXCEEDED]
    S5 -- YES --> S6{Stage 6: Amount <= Auto-Approval Limit?}
    S6 -- YES --> EVAL_RISK_LOW[Evaluate FRAUDGUARD Risk Score]
    S6 -- NO --> EVAL_RISK_HIGH[Evaluate FRAUDGUARD Risk Score]
    EVAL_RISK_LOW --> D1{Risk Score <= 35?}
    D1 -- YES --> ALLOW[ALLOW: Auto-Approve & Execute]
    D1 -- NO --> REVIEW[REVIEW: Escalate to Approval Center]
    EVAL_RISK_HIGH --> D2{Risk Score >= 70?}
    D2 -- YES --> BLOCK6[BLOCK: ERR_HIGH_FRAUD_RISK]
    D2 -- NO --> REVIEW
```

---

## 3. Decision Trace Schema

Every decision rendered by AGENTGUARD produces a standardized structured payload:

```json
{
  "decision_id": "dec_9f8a7b6c-5d4e-3f2a",
  "transaction_id": "intent_7f8a9b0c-1d2e-3f4a",
  "agent_id": "agt_8f9b2c3a-4e1d-4a5b",
  "risk_score": 18,
  "risk_level": "LOW_RISK",
  "policy_result": "PASS",
  "triggered_rules": ["RULE_SINGLE_LIMIT_PASS", "RULE_MCC_ALLOWED"],
  "model_version": "fraudguard_xgb_v1.4.2",
  "explanation": "Transaction APPROVED. Amount (₹2,500) is within auto-approval threshold ₹5,000. Category 'Electronics' is allowed.",
  "timestamp": "2026-08-24T21:15:00Z",
  "decision_latency_ms": 12.4
}
```
