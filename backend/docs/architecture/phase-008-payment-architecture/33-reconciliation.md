# AGENTPAY — 33: Internal vs Razorpay Gateway Settlement Reconciliation

## 1. Dual Reconciliation Architecture

```
[ Internal DB Payment Records ]  <---(Reconciliation Comparison)--->  [ Razorpay Settlement Batch API ]
                                                │
                                  ┌─────────────┴─────────────┐
                                  ▼                           ▼
                             [ MATCHED ]              [ DISCREPANCY ]
                                                              │
                                                     [ Alert & Audit Log ]
```
