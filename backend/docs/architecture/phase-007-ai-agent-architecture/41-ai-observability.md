# AGENTPAY — 41: OpenTelemetry Distributed Tracing (`trace_id`, `agent_id`)

## 1. AI Telemetry Standards

Every AI agent task step emits OpenTelemetry span attributes: `trace_id`, `task_id`, `agent_id`, `tenant_id`, `model_provider`, `model_version`, `prompt_tokens`, `completion_tokens`, `tool_invoked`, `decision_id`, `latency_ms`.
