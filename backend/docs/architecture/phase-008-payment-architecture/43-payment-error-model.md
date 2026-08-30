# AGENTPAY — 43: 13 Normalized Internal Payment Error Categories

## 1. Internal Payment Error Taxonomy

1. `VALIDATION_ERROR`: Schema validation failure.
2. `AUTHORIZATION_ERROR`: Missing or expired authorization token.
3. `POLICY_ERROR`: Single limit or daily budget cap breached.
4. `RISK_ERROR`: High fraud risk score ($> 70$).
5. `PROVIDER_ERROR`: Razorpay 5xx gateway error.
6. `NETWORK_ERROR`: Network socket connection failure.
7. `TIMEOUT`: 5,000ms provider gateway timeout.
8. `DUPLICATE`: Idempotency key reuse conflict.
9. `STATE_CONFLICT`: Illegal state machine transition attempt.
10. `INSUFFICIENT_FUNDS`: Card/UPI bank account balance insufficient.
11. `WEBHOOK_ERROR`: Webhook signature verification failure.
12. `RECONCILIATION_ERROR`: Settlement discrepancy detected.
13. `UNKNOWN`: Unresolved provider state requiring verification.
