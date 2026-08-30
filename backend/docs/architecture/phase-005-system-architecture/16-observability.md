# AGENTPAY — 16: Structured JSON Logs, OpenTelemetry & Prometheus Tracing

## 1. Observability Architecture

```mermaid
graph TD
    subgraph Instrumentation Sources
        GW[API Gateway]
        POLICY[AGENTGUARD Engine]
        FRAUD[FRAUDGUARD AI Service]
        PAYMENT[Payment Orchestrator]
    end

    subgraph Telemetry Collectors
        LOG_COLLECTOR[Structured JSON Logger]
        PROM_EXPORTER[Prometheus Metrics Exporter]
        OTEL_TRACER[OpenTelemetry Distributed Tracer]
    end

    subgraph Monitoring & Visualization
        GRAFANA[Grafana Dashboard]
        PROMETHEUS_SERVER[Prometheus TSDB]
        JAEGER[Jaeger Trace Viewer]
    end

    GW & POLICY & FRAUD & PAYMENT --> LOG_COLLECTOR & PROM_EXPORTER & OTEL_TRACER
    LOG_COLLECTOR --> GRAFANA
    PROM_EXPORTER --> PROMETHEUS_SERVER
    OTEL_TRACER --> JAEGER
    PROMETHEUS_SERVER --> GRAFANA
```

---

## 2. Mandatory Correlation Identifiers

Every log entry and trace span includes seven correlation tags:

```text
trace_id       : OpenTelemetry W3C Distributed Trace Header
request_id     : API Edge Ingress Request UUID
transaction_id : Payment Intent UUID
agent_id       : AI Agent UUID
tenant_id      : User / Organization Owner UUID
payment_id     : Razorpay Payment ID
decision_id    : AGENTGUARD Authorization Decision UUID
```
