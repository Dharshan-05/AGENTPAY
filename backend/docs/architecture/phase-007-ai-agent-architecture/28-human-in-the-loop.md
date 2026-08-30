# AGENTPAY — 28: Interactive Approval Center Escalation & Timeout Protocols

## 1. Approval Center Protocol

Intents returning `REVIEW` transition to `PENDING_APPROVAL` with a 15-minute TTL:

1. Intent metadata, XAI explanation text, and top risk factors pushed to Approval Center UI via WebSocket.
2. User inspects card and clicks **APPROVE** or **REJECT**.
3. Approving acquires an atomic lock, transitions state to `AUTHORIZED`, and resumes payment settlement.
4. Unanswered requests expire after 15 minutes, transitioning to `EXPIRED`.
