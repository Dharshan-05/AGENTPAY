# AGENTPAY — 32: Available vs Pending vs Reserved Balance Controls

## 1. Balance Partitioning

* **`Available Balance`**: Funds available for immediate agent purchase.
* **`Reserved Balance`**: Funds locked in `AUTHORIZED` payment intents.
* **`Pending Balance`**: Funds awaiting Razorpay webhook settlement confirmation.
* **`Settled Balance`**: Fully cleared funds available for merchant withdrawal.
