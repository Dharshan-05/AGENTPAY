# ATIM Phase 13 Architecture — Production Observability, Distributed Tracing & Telemetry

## Executive Summary
**ATIM Phase 13** establishes a production-grade observability and telemetry architecture for the **AgentPay Transaction Intelligence Model (ATIM)** infrastructure.

Phase 13 introduces:
1. **Correlation ID & Context Propagation (`CorrelationContext`)**: Generates unique request correlation IDs (`corr_01J...`) and context objects propagating across all pipeline stages.
2. **Telemetry Sanitizer (`TelemetrySanitizer`)**: Redacts Bearer tokens, API keys, passwords, credit card numbers, UPI IDs, and PII before logging or tracing.
3. **Structured JSON Logging (`ATIMStructuredLogger`)**: Emits structured JSON events capturing request metadata, latencies, model selections, token counts, and security decisions.
4. **Prometheus Metrics Collector (`ATIMMetricsCollector`)**: Aggregates `atim_requests_total`, `atim_llm_latency_seconds`, `atim_security_blocks_total`, and `atim_cost_total` with low label cardinality.
5. **OpenTelemetry-Compatible Distributed Tracing (`ATIMTracer`)**: Creates spans for `atim.request`, `atim.security`, `atim.routing`, `atim.llm`, `atim.agentguard`, `atim.fraudguard`, `atim.hitl`.
6. **Health & Readiness Engine (`ATIMHealthChecker`)**: Separates liveness, readiness, and dependency health checks (PostgreSQL, Redis, Provider API, Circuit Breaker).

---

## Observability Architecture

```text
ATIM PIPELINE STAGES
 (Security → Routing → LLM → Intent → Planning → Validation → AGENTGUARD → FRAUDGUARD → HITL)
                                  │
                                  ▼
                     CORRELATION CONTEXT (corr_01J...)
                                  │
                                  ▼
                         TELEMETRY SANITIZER
             (Redacts Bearer, Keys, Cards, UPI, PII)
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
   STRUCTURED LOGS         PROMETHEUS METRICS      DISTRIBUTED TRACES
  (JSON Format)           (Bounded Labels)        (OpenTelemetry Spans)
```
