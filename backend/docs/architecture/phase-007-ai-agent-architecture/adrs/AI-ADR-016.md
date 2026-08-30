# AI-ADR-016: OpenTelemetry W3C Distributed AI Tracing

## Context & Problem Statement
Tracing multi-agent execution steps and token costs across distributed microservices requires standardized correlation tags.

## Decision
Standardize on OpenTelemetry W3C distributed trace context headers (`trace_id`, `agent_id`, `decision_id`) across all LLM inference and tool invocation spans.

## Consequences & Trade-Offs
* **Benefits**: Instant end-to-end visualization of agent execution paths in Jaeger/Grafana.
* **Trade-Offs**: Requires instrumenting custom span attributes in TypeScript and Python services.
