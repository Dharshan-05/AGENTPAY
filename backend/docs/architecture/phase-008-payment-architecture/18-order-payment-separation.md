# AGENTPAY — 18: Structural Decoupling of Orders vs Payment Settlements

## 1. Decoupled Entities Architecture

`Order` represents the commercial agreement (purchased items, merchant, tax), while `Payment` represents the financial settlement.

```
[ Order: ord_3f2a1b0c ] ──(1:N)──> [ PaymentIntent: intent_1 ] ──(FAILED)
                         └──(1:N)──> [ PaymentIntent: intent_2 ] ──(SUCCESS)
```

Decoupling allows an order to be retried via a new `PaymentIntent` without mutating the underlying commercial order record.
