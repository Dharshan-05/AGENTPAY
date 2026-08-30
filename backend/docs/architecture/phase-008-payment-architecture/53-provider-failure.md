# AGENTPAY — 53: Provider Outage & Circuit Breaker Degradation Playbook

## 1. Provider Outage Degradation Playbook

1. **Detection**: 5 consecutive Razorpay API 5xx errors or timeouts within 60 seconds.
2. **Circuit Breaker Activation**: Opens circuit breaker for 30 seconds (`ERR_GATEWAY_CIRCUIT_OPEN`).
3. **Inflight Intent Handling**: Active intents transition safely to `PAYMENT_STATUS_UNKNOWN`.
4. **User Communication**: Ingress API returns HTTP 503 `Payment Gateway Temporarily Unavailable`.
