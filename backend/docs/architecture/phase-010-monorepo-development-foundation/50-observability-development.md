# AGENTPAY — 50: `@agentpay/observability` Tracing & Logger Setup

## 1. Observability Package

* `@agentpay/observability` encapsulates OpenTelemetry Node.js SDK setup and structured Winston logger instance.
* Spans inject `trace_id`, `request_id`, `tenant_id`, and `agent_id` into output JSON logs.
