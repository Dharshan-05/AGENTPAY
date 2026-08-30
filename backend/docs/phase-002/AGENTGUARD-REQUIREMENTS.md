# AGENTPAY — AgentGuard Requirements

## 1. Overview

**AGENTGUARD** is the policy and security authorization gatekeeper of AGENTPAY. It evaluates every incoming `PAYMENT INTENT` against explicit user-configured spending limits, merchant restrictions, category rules, temporal windows, and agent state boundaries.

---

## 2. Requirement Baseline

### 2.1 Policy Rule Evaluation Types
* **REQ-AGD-001**: AGENTGUARD shall evaluate six mandatory deterministic policy rule checks:
  1. **Agent State Check**: Verify agent is in `ACTIVE` state.
  2. **Single Transaction Limit Check**: Verify intent amount $\le$ single transaction ceiling.
  3. **Cumulative Spending Budget Check**: Verify intent amount + daily spending $\le$ daily limit.
  4. **Category Restriction Check**: Verify target Merchant Category Code (MCC) is allowed and NOT in blocked list.
  5. **Merchant Restrictions Check**: Verify target merchant domain is NOT in user blacklist.
  6. **Temporal Rule Check**: Verify current timestamp falls within active operating hours window.

### 2.2 Rule Precedence & Conflict Resolution
* **REQ-AGD-002**: AGENTGUARD shall evaluate policy rules according to strict security precedence order:
  $$\text{Emergency Stop} > \text{Revocation/Pause} > \text{Category Blacklist} > \text{Single Limit} > \text{Daily Budget} > \text{Auto-Approval Ceiling}$$
* **REQ-AGD-003**: If any negative restrictive rule (e.g. Category Blacklist or Limit Exceeded) is triggered, AGENTGUARD shall immediately evaluate to `BLOCK` regardless of positive whitelist matches. Restrictive rules ALWAYS take precedence over permissive rules.

### 2.3 Decision Outputs
* **REQ-AGD-004**: AGENTGUARD shall output exactly one of four canonical decisions:
  * `ALLOW`: All rules satisfied and amount $\le$ auto-approval ceiling.
  * `REVIEW`: Basic rules satisfied, but amount exceeds auto-approval ceiling or exhibits boundary warnings.
  * `CHALLENGE`: Requires step-up authentication from human user.
  * `BLOCK`: Violates hard policy constraints (forbidden category, limit exceeded, revoked agent).

### 2.4 Policy Cache Management & Latency
* **REQ-AGD-005**: AGENTGUARD policy evaluations shall complete in $\le 15\text{ ms}$ at $p_{99}$ latency.
* **REQ-AGD-006**: User policy definitions shall be cached at edge API gateways (via Redis). When a user updates policy rules, the system shall invalidate active policy caches within $< 50\text{ ms}$.
