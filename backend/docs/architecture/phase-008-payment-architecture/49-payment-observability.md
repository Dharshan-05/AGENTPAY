# AGENTPAY — 49: Distributed OpenTelemetry Tracing (`payment_id`)

## 1. Observability Tracing Tags

Every payment operation emits OpenTelemetry spans containing: `trace_id`, `request_id`, `payment_intent_id`, `payment_id`, `provider_payment_id`, `agent_id`, `tenant_id`, `decision_id`.
