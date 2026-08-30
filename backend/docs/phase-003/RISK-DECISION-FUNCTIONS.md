# AGENTPAY — Risk Decision Functional Specifications

## 1. Overview

Risk Decision functions map calculated `RISK SCORE` metrics, AGENTGUARD policy checks, and user risk tolerance configurations into final authorization decisions (`ALLOW`, `REVIEW`, `CHALLENGE`, `BLOCK`).

---

## 2. Specifications

### FR-RISK-001: 4-Tier Risk Decision Matrix & Threshold Mapping
* **FR ID**: `FR-RISK-001`
* **Title**: Configurable 4-Tier Risk Decision Matrix & Action Mapping
* **Source**: `REQ-FRAUD-003`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Decision Engine (`SYSTEM`)
* **Goal**: Render final authorization decision based on composite policy results and risk levels.
* **Preconditions**: AGENTGUARD policy results and FRAUDGUARD risk score calculated.
* **Trigger**: Risk scoring completion.
* **Inputs**: `policy_decision` (`ALLOW` / `REVIEW`), `risk_score` (0-100), `user_risk_tolerance` (`CONSERVATIVE` / `BALANCED` / `AGGRESSIVE`).
* **Main Flow**:
  1. System checks `policy_decision`. If AGENTGUARD output `BLOCK`, final decision is `BLOCK`.
  2. System evaluates `risk_level` against configurable decision mapping table:
     * **LOW_RISK (00 - 35)**: If policy output `ALLOW`, final decision = `ALLOW`.
     * **MEDIUM_RISK (36 - 69)**: Final decision = `REVIEW` (Escalate to Approval Center).
     * **HIGH_RISK (70 - 89)**: Final decision = `BLOCK`.
     * **CRITICAL_RISK (90 - 100)**: Final decision = `BLOCK` + Dispatch Security Alert + Auto-Suspend Agent State.
  3. System passes final decision to XAI Engine (`FR-XAI-001`) for explanation generation.
* **Business Rules**: `BR-004`, `BR-006`.
* **Outputs**: Authorization Decision payload (`final_decision`, `risk_level`, `actions_triggered`).
* **Audit Events**: `EVENT_DECISION_RENDERED`.
* **Acceptance Criteria**: `AC-POLICY-003`, `AC-FRAUD-001`.
* **Dependencies**: `FR-AGD-001`, `FR-FRD-002`.
