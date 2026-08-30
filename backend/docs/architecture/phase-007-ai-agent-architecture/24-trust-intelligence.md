# AGENTPAY — 24: Dynamic Agent Trust Engine (0-100 Scale)

## 1. Trust Score Calculation

Every AI agent maintains a dynamic `Trust Score` (0-100):

$$\text{TrustScore} = \text{BaseScore} + \text{HistoryBonus} - \text{ViolationPenalties} - \text{VelocityPenalties}$$

* **90–100 (High Trust)**: Eligible for auto-approval up to single limit cap.
* **70–89 (Trusted)**: Auto-approval up to standard limit.
* **40–69 (Medium Trust)**: Requires secondary risk evaluation.
* **0–39 (Low Trust)**: Intent proposals held for human `REVIEW` or `BLOCK`.
