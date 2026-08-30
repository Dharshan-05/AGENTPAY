# AGENTPAY — 41: FRAUDGUARD ML Risk Score Integration

## 1. ML Risk Scoring Integration

FRAUDGUARD extracts 12 real-time feature dimensions, evaluating transaction risk in $< 30\text{ ms}$:

* `RISK SCORE 0-35 (LOW)`: Eligible for auto-approval.
* `RISK SCORE 36-69 (MEDIUM)`: Escalates to Approval Center UI (`PENDING_APPROVAL`).
* `RISK SCORE 70-100 (HIGH)`: Blocks transaction immediately (`BLOCKED`).
