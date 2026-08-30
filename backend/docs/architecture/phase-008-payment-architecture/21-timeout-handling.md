# AGENTPAY — 21: Provider Gateway Timeout SLA (5,000ms Hard Cap)

## 1. Timeout Boundary Rules

* **Hard Provider SLA**: Outbound calls to Razorpay API enforce a strict 5,000ms HTTP socket timeout.
* **Circuit Breaker Trigger**: 5 consecutive timeouts open the gateway circuit breaker for 30s (`ERR_GATEWAY_CIRCUIT_OPEN`).
* **No Implicit Retry**: Un-responded requests transition state to `PAYMENT_STATUS_UNKNOWN` rather than auto-retrying.
