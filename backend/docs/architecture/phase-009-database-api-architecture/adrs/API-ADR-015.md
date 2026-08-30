# API-ADR-015: OpenTelemetry Distributed W3C API Tracing Instrumentation

## 1. Context & Problem Statement
Tracking request latency and troubleshooting errors across distributed services.

## 2. Decision
Instrument OpenTelemetry SDK across all API controllers, injecting W3C `traceparent` context headers into downstream calls.

## Consequences & Trade-Offs
* **Benefits**: End-to-end trace visibility in Grafana/Jaeger.
* **Trade-Offs**: Requires adding tracing middleware to API routes.
