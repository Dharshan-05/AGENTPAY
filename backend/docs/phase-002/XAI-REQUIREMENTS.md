# AGENTPAY — Explainable AI (XAI) Requirements

## 1. Overview

The **XAI Engine** is responsible for generating transparent, human-understandable, and machine-auditable explanations for every transaction decision made by AGENTGUARD and FRAUDGUARD.

---

## 2. Requirement Baseline

### 2.1 Feature Attribution & Importance Ranking
* **REQ-XAI-001**: For every evaluated transaction, the XAI Engine shall calculate numerical feature contributions (e.g. via SHAP values or feature weight vectors) ranking the top 3 factors driving the risk score.
* **REQ-XAI-002**: Feature attributions shall explicitly categorize whether each factor increased risk (risk push) or decreased risk (trust push).

### 2.2 Natural Language Summary Generation
* **REQ-XAI-003**: The XAI Engine shall synthesize complex risk scores, policy evaluation results, and feature rankings into a concise, human-readable natural language sentence.
* **REQ-XAI-004**: Natural language explanations shall follow standardized templates for clarity and consistency across decisions (`ALLOW`, `REVIEW`, `BLOCK`).

### 2.3 Decision Trace Structure
* **REQ-XAI-005**: The system shall assemble a structured `decision_trace` object for every transaction containing:
  * `timestamp`: Precise ISO 8601 execution timestamp.
  * `intent_id`: Unique payment intent identifier.
  * `agent_id`: Initiating agent identifier.
  * `policy_results`: Array of evaluated AGENTGUARD rules and individual pass/fail statuses.
  * `risk_summary`: Computed `risk_score`, `risk_level`, and `fraud_probability`.
  * `top_risk_factors`: Top ranked feature attributions with impact weights.
  * `final_decision`: Rendered decision (`ALLOW`, `REVIEW`, `CHALLENGE`, `BLOCK`).
  * `natural_language_explanation`: Generated summary sentence.

### 2.4 Audit & UI Integration
* **REQ-XAI-006**: The decision trace and natural language explanation shall be embedded directly into the Approval Center UI when a transaction requires human review.
* **REQ-XAI-007**: The decision trace shall be permanently stored alongside the transaction record in the immutable audit trail log.
