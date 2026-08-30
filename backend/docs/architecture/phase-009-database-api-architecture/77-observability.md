# AGENTPAY — 77: OpenTelemetry Distributed W3C API Tracing Specs

## 1. W3C Trace Context Standard

All API requests accept and propagate W3C Distributed Tracing headers (`traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`). Spans inject `tenant_id`, `actor_id`, `agent_id`, and `payment_id` attributes into OpenTelemetry collectors.
