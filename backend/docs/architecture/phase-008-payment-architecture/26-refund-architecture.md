# AGENTPAY — 26: Full & Partial Refund Execution Architecture

## 1. Refund Pipeline

```
[ Refund Request ] ──> [ Validate Refundable Balance ] ──> [ AGENTGUARD Policy ] ──> [ Razorpay Refund API ] ──> [ Ledger Reversal ]
```

Refund requests require explicit human user or AGENTGUARD authorization, validating that cumulative refunds never exceed original payment amounts.
