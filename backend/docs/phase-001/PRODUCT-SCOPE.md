# AGENTPAY — Product Scope

## 1. System Scope Overview

**AGENTPAY** acts as the central middleware security, authorization, risk analysis, and execution layer operating between autonomous AI AGENT entities and underlying financial settlement networks. 

The primary scope of AGENTPAY encompasses the full operational pipeline from **Payment Intent Creation** through **Policy Check**, **Risk Evaluation**, **Explainable Decisioning**, **Authorization/Escalation**, **Payment Execution**, and **Immutable Audit Logging**.

---

## 2. Core Components in Scope

### 2.1 AGENTPAY Core Platform
* **Payment Intent Management**: API surface allowing AI AGENT entities to submit structured payment requests (`PAYMENT INTENT`).
* **Payment Execution Abstraction**: Unified gateway adapter interfacing with payment processors (e.g., UPI, Razorpay, Mock Banking Adapters).
* **State Engine & Lifecycle Manager**: Tracking intent transitions (`CREATED`, `POLICIED`, `SCORED`, `PENDING_APPROVAL`, `AUTHORIZED`, `EXECUTED`, `REJECTED`, `FAILED`).

### 2.2 AGENTGUARD (Policy Engine & Identity Layer)
* **Agent Registration & Lifecycle**: Identity assignment, cryptographic key pairs, revocation status, and metadata tagging.
* **Deterministic Policy Engine**: Evaluation of spending limits, merchant restrictions, category rules, temporal rules, and velocity checks.
* **Permission Verification**: Validating whether an AI AGENT is authorized by its human owner to perform actions matching the submitted intent.

### 2.3 FRAUDGUARD (Risk & Anomaly Engine)
* **Risk Feature Extraction**: Calculating real-time signals across transaction amount, frequency, merchant trustworthiness, contextual timing, and behavioral deviations.
* **Machine Learning Scoring**: Evaluating statistical anomaly models to output a normalized `RISK SCORE` (0 - 100) and `FRAUD PROBABILITY`.
* **Deterministic Risk Rules**: Applying static safeguards to ensure safety boundaries are enforced independently of model outputs.

### 2.4 XAI (Explainable AI Engine)
* **Feature Attribution**: Identifying top contributing signals behind every risk assessment (e.g., using SHAP values or rule weights).
* **Natural Language Explanation**: Translating complex numerical scores and rule triggers into human-readable sentences for administrators and end-users.
* **Decision Trace Generation**: Generating audited step-by-step logs explaining exactly why a transaction was approved, challenged, or blocked.

### 2.5 Approval Center & Notifications
* **Human-in-the-Loop Workflow**: Real-time escalation portal for transactions flagged for `REVIEW` or `CHALLENGE`.
* **Notification Dispatcher**: Alerting users via webhook, email, or web dashboard when authorization intervention is required or critical anomalies are detected.

### 2.6 Audit Trail & Dashboard UI
* **Immutable Audit Trail**: Append-only log recording every evaluation step, policy match, risk score, XAI rationale, human decision, and execution status.
* **Admin & User Dashboards**: Visual reporting over agent portfolios, transaction histories, policy configurations, and real-time risk telemetry.

---

## 3. System Boundary & Touchpoints

```
[ OUTSIDE SCOPE ]                 [ AGENTPAY BOUNDARY ]                [ OUTSIDE SCOPE ]
+-------------------+           +------------------------+           +-------------------+
|  AI Agent Prompt  | --------> |  Payment Intent API    | --------> |  Bank / Gateway   |
|  & Internal Logic |           |  AgentGuard Policy     |           |  (UPI / Razorpay  |
|                   |           |  FraudGuard Engine     |           |   Settlement)     |
+-------------------+           |  XAI Engine            |           +-------------------+
                                |  Approval Center       |
                                |  Immutable Audit Log   |
                                +------------------------+
```

### In-Scope Boundaries
* Ingestion of payment intent payloads from AI AGENTs.
* Authentication and policy validation of the requesting AI AGENT.
* Real-time risk evaluation and XAI output generation.
* Authorization decision rendering (`ALLOW`, `REVIEW`, `CHALLENGE`, `BLOCK`).
* Orchestration of human approval workflows.
* Forwarding approved intents to payment processor adapters.
* Recording immutable audit logs.

### Out-of-Scope Boundaries (Platform Boundaries)
* Direct hosting or execution of the AI AGENT's internal LLM reasoning or prompt engines.
* End-user bank account custody (AGENTPAY is a software control layer, not a direct banking vault).
* Complex multi-country forex cross-border clearing for MVP.
* Physical card issuance or ATM network operation.

---

## 4. Scope Bounding Principles

1. **Deterministic Authority**: Financial authorization is ultimately determined by deterministic policy rules and verified risk thresholds, not raw LLM outputs.
2. **Strict Identity Verification**: Unverified or unauthenticated agents are rejected at the edge before policy or fraud processing occurs.
3. **Idempotency Guarantee**: Every `PAYMENT INTENT` must be uniquely identifiable and idempotent to prevent double-spending or agent retry loops.
