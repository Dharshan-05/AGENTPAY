# MONO-ADR-022: OpenTelemetry Tracing & Winston JSON Logging Package

## 1. Context & Problem Statement
Standardizing structured logging and distributed tracing instrumentation across TypeScript and Python services.

## 2. Decision
Publish `@agentpay/observability` to encapsulate OpenTelemetry Node.js SDK setup and Winston JSON logger formatting.

## 3. Consequences & Trade-Offs
* **Benefits**: End-to-end W3C trace context propagation across all microservice boundaries.
* **Trade-Offs**: Requires initializing tracing SDK on application startup.
