# AGENTPAY — Explainable AI (XAI) Functional Specifications

## 1. Overview

XAI Engine functions specify feature attribution calculation, top factor weight ranking, natural language summary synthesis, and decision trace object assembly.

---

## 2. Specifications

### FR-XAI-001: Top-3 Feature Attribution Weight Ranking
* **FR ID**: `FR-XAI-001`
* **Title**: Feature Attribution Weight Ranking & Risk Push/Trust Push Vector Analysis
* **Source**: `REQ-XAI-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: XAI Engine (`XAI`)
* **Goal**: Rank top feature attributions driving risk decisions for every transaction.
* **Preconditions**: Risk score and feature vector calculated.
* **Trigger**: Decision rendering completion.
* **Inputs**: Feature Vector $\mathbf{x}$, Model Weights $W$, Computed `risk_score`.
* **Main Flow**:
  1. XAI Engine calculates linear/SHAP feature contribution values ($C_i = w_i \times x_i$).
  2. Engine sorts feature contributions by absolute magnitude $|C_i|$.
  3. Engine extracts top 3 features (e.g. `amount_z_score`, `merchant_trust_score`, `category_restriction`).
  4. Engine assigns impact classification:
     * Positive impact ($C_i > 0$): `Risk Push` (Increased Risk).
     * Negative impact ($C_i < 0$): `Trust Push` (Decreased Risk).
* **Outputs**: Array of Top-3 Feature Attribution objects with weights and impact tags.
* **Audit Events**: `EVENT_XAI_ATTRIBUTION_CALCULATED`.
* **Acceptance Criteria**: `AC-XAI-001`.
* **Dependencies**: `FR-FRD-002`, `FR-RISK-001`.

---

### FR-XAI-002: Natural Language Summary Text Generation
* **FR ID**: `FR-XAI-002`
* **Title**: Natural Language Summary Text Generation
* **Source**: `REQ-XAI-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: XAI Engine (`XAI`)
* **Goal**: Synthesize plain-language natural text explanation sentences for user and audit log inspection.
* **Preconditions**: Decision rendered; top features ranked via `FR-XAI-001`.
* **Trigger**: Feature attribution ranking completion.
* **Inputs**: `final_decision`, `risk_score`, `top_features`, `policy_results`.
* **Main Flow**:
  1. Engine selects explanation template based on `final_decision`:
     * **ALLOW**: *"Transaction APPROVED. Amount [amount] is within auto-approval threshold [threshold]. Category '[category]' is explicitly allowed. Merchant trust rating is high ([score]/100)."*
     * **REVIEW**: *"Transaction flagged for HUMAN REVIEW. Amount [amount] exceeds auto-approval threshold [threshold]. Target merchant has neutral trust rating ([score]/100)."*
     * **BLOCK**: *"Transaction BLOCKED. Exceeds single limit [limit] by [percent]%. Category '[category]' is explicitly forbidden by user policy. Merchant flagged for high fraud probability."*
  2. Engine injects exact transaction amounts, thresholds, categories, and merchant scores into template variables.
  3. Engine outputs formatted text string (`natural_language_explanation`).
* **Outputs**: Natural Language Explanation string.
* **Audit Events**: `EVENT_XAI_SUMMARY_GENERATED`.
* **Acceptance Criteria**: `AC-XAI-001`.
* **Dependencies**: `FR-XAI-001`.
