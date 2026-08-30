# AGENTPAY — 10: AGENTGUARD Security Gate & Policy Precedence

## 1. AGENTGUARD Precedence Order

AGENTGUARD enforces policy checks in strict security precedence:

$$\text{Stage 1: Emergency Stop} > \text{Stage 2: Agent Status} > \text{Stage 3: Category Blacklist} > \text{Stage 4: Single Limit} > \text{Stage 5: Daily Budget} > \text{Stage 6: Auto-Approval Ceiling}$$

---

## 2. Fail-Closed Guarantee

If any stage fails, execution short-circuits instantly, emitting a `BLOCK` decision and security event log. If an internal policy evaluation service fails or times out, AGENTGUARD defaults to `BLOCK` or `REVIEW` (`Fail Closed`).
