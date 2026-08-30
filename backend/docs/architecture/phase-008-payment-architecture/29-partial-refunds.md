# AGENTPAY — 29: Cumulative Refund Amount Tracking & Over-Refund Guard

## 1. Over-Refund Invariant Check

$$\sum \text{RefundAmounts} \le \text{OriginalPaymentAmount}$$

$$\text{RefundableBalance} = \text{OriginalAmount} - \sum \text{SettledRefunds} - \sum \text{PendingRefunds}$$

Attempts to request a refund where $\text{RequestedAmount} > \text{RefundableBalance}$ fail deterministically with HTTP 422 (`ERR_REFUND_EXCEEDS_BALANCE`).
