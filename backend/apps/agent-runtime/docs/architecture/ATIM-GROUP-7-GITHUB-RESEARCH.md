# ATIM Group 7 — GitHub Architecture Research & Pattern Adaptation

## Executive Summary
This document analyzes open-source observability, distributed tracing, metric aggregation, and resilience engineering frameworks to inform the architectural design of **ATIM Group 7 (Phases 13 & 14)**.

In accordance with AGENTPAY core invariants:
- **LLM is an UNTRUSTED PROPOSAL ENGINE**.
- **Observability and reliability mechanisms MUST NEVER bypass AGENTGUARD, FRAUDGUARD, HITL, or financial authorization**.
- **Telemetry fails closed if secret redaction fails**.

---

## Comparative Framework Analysis & Classification

| Framework | Primary Patterns & Architecture | AGENTPAY Adaptation Strategy | Classification | Justification & Security Boundaries |
|---|---|---|---|---|
| **OpenTelemetry Python / FastAPI** | Distributed tracing, correlation IDs (`trace_id`, `span_id`), context propagation, structured span creation | Implement `ATIMTracingManager` creating spans for ATIM pipeline stages (`atim.security`, `atim.routing`, `atim.agentguard`). | **ADAPT** | Adopt span creation & context propagation; REJECT placing raw prompts, API keys, or PII into span attributes. |
| **Prometheus Python Client** | Counters, Histograms, Gauges for requests, latencies, error rates, token expenditures | Implement `ATIMMetricsCollector` collecting `atim_requests_total`, `atim_llm_latency_seconds`, `atim_security_blocks_total`. | **ADAPT** | Adopt standardized metrics; REJECT high-cardinality labels (e.g., prompt text, transaction IDs, free-form errors). |
| **LiteLLM / Guardrails Observability** | Structured JSON logging, provider cost accounting, automated secret redaction | Implement `TelemetrySanitizer` reusing existing `PromptGuard` secret/PII detectors. | **ADAPT** | Adopt structured JSON logging & sanitization; REJECT exporting unredacted secrets or cloud payload dumps. |
| **Resilience4j / Netflix Chaos Monkey** | Fault injection, dependency failure simulation, circuit breaker chaos, recovery testing | Implement `FailureInjector` abstraction for controlled test-only fault injection (LLM timeout, DB error, Redis drop). | **ADAPT** | Adopt deterministic failure injection interface; REJECT enabling chaos controls in production or exposing injection APIs to users/LLMs. |

---

## Detailed Pattern Decisions

### 1. Observability & Telemetry Sanitization (Phase 13)
- **REUSE**: `PromptGuardService`, `ATIMSecretDetector`, `ATIMPIIDetector` from Phase 4.
- **ADAPT**: Implement `TelemetrySanitizer` to sanitize all trace attributes, metric labels, and JSON structured logs prior to export.
- **REJECT**: External cloud logging of raw prompts, credit card numbers, or authorization tokens.

### 2. Distributed Tracing & Correlation IDs (Phase 13)
- **ADAPT**: Generate correlation ID `corr_01J...` at entry point `/api/v1/atim/analyze` and propagate through all downstream pipeline spans.
- **REJECT**: Using user prompts or payment payloads as correlation identifiers.

### 3. Reliability & Fault Injection Abstraction (Phase 14)
- **ADAPT**: Build test-only `FailureInjector` allowing injection of simulated provider timeouts, HTTP 429/500 errors, database connection drops, and Redis failures.
- **REJECT**: User-controlled or LLM-controlled failure injection. `ATIM_FAILURE_INJECTION_ENABLED` must default to `False`.
