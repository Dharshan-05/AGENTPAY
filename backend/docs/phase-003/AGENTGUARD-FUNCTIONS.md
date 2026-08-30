# AGENTPAY — AGENTGUARD Policy Engine Functional Specifications

## 1. Overview

**AGENTGUARD** is the policy and security authorization gatekeeper of AGENTPAY. It executes deterministic policy evaluations in strict precedence order to answer the authoritative question: *"Is this AI AGENT permitted to execute this transaction under current user policies and system state?"*

---

## 2. Specifications

### FR-AGD-001: 6-Stage Policy Precedence Evaluation Pipeline
* **FR ID**: `FR-AGD-001`
* **Title**: AGENTGUARD 6-Stage Precedence Evaluation Pipeline
* **Source**: `REQ-AGD-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: AGENTGUARD System (`AGENTGUARD`)
* **Goal**: Evaluate incoming payment intent through six deterministic policy stages in strict precedence order.
* **Preconditions**: Request authenticated via `FR-AUTH-003`; intent schema validated.
* **Trigger**: Payment intent ingestion into AGENTGUARD pipeline stage.
* **Inputs**: `intent` object, `agent` state object, `user_policy` object.
* **Main Flow**:
  1. **Stage 1 (Emergency Stop Check)**: Check if user Emergency Stop is engaged. If YES, output `BLOCK` (`ERR_EMERGENCY_STOP_ACTIVE`).
  2. **Stage 2 (Agent State Check)**: Verify `agent.state == ACTIVE`. If NO, output `BLOCK` (`ERR_AGENT_NOT_ACTIVE`).
  3. **Stage 3 (Category Blacklist Check)**: Check if `intent.category` is in `blocked_categories`. If YES, output `BLOCK` (`ERR_CATEGORY_BLOCKED`).
  4. **Stage 4 (Single Limit Check)**: Compare `intent.amount` against `max_single_amount`. If EXCEEDED, output `BLOCK` (`ERR_SINGLE_LIMIT_EXCEEDED`).
  5. **Stage 5 (Cumulative Budget Check)**: Compare `intent.amount + daily_spent` against `daily_budget`. If EXCEEDED, output `BLOCK` (`ERR_DAILY_BUDGET_EXCEEDED`).
  6. **Stage 6 (Auto-Approval Threshold Check)**: Compare `intent.amount` against `auto_approval_threshold`.
     * If `intent.amount <= threshold`: Output preliminary decision `ALLOW`.
     * If `intent.amount > threshold`: Output preliminary decision `REVIEW`.
* **Alternative Flows**:
  * *AF-1 (Stage Failure)*: Execution short-circuits immediately upon first failed Stage (1-5), emitting `BLOCK` decision without executing subsequent stages.
* **Business Rules**: `BR-003`, `BR-005`, `BR-006`.
* **Precedence Rules**: Stage 1 > Stage 2 > Stage 3 > Stage 4 > Stage 5 > Stage 6. Restrictive rules ALWAYS override permissive rules.
* **Performance SLA**: Complete pipeline evaluation in $\le 15\text{ ms}$ ($p_{99}$).
* **Outputs**: AGENTGUARD Policy Result payload: `decision` (`ALLOW`, `REVIEW`, `CHALLENGE`, `BLOCK`), `failed_stage` (integer or null), `reason_code` (string).
* **Audit Events**: `EVENT_AGENTGUARD_EVALUATION_COMPLETED`.
* **Acceptance Criteria**: `AC-POLICY-001`, `AC-POLICY-002`, `AC-POLICY-003`.
* **Dependencies**: `FR-AUTH-003`, `FR-POLICY-001`, `FR-POLICY-002`, `FR-POLICY-003`.
