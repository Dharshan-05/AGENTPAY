# ATIM Phase 14 — Chaos Test Matrix

## 1. Chaos Scenario Definitions

| Scenario ID | Dependency | Fault Type | Expected System Behavior | Security Invariant Preserved |
|---|---|---|---|---|
| **CHAOS-01** | LLM Provider | Timeout / Connection Reset | Retry $\rightarrow$ Fallback to Secondary Model $\rightarrow$ Rule Engine | Financial execution remains safe |
| **CHAOS-02** | LLM Provider | HTTP 429 Rate Limit | Circuit Breaker triggers $\rightarrow$ Fallback Model | Unsafe model never selected |
| **CHAOS-03** | LLM Provider | Malformed JSON / Invalid Schema | Plan Validator rejects plan $\rightarrow$ Rule Engine | Invalid plan never executed |
| **CHAOS-04** | PostgreSQL | Connection Failure / Pool Exhaustion | Service returns 503 $\rightarrow$ FAIL CLOSED | No partial payment state created |
| **CHAOS-05** | Redis Cache | Redis Drop / Connection Timeout | Cache bypass $\rightarrow$ Direct DB query or FAIL CLOSED | Redis failure never authorizes |
| **CHAOS-06** | Telemetry | Exporter Failure / Queue Full | Telemetry logged locally $\rightarrow$ Transaction proceeds safely | Observability loss doesn't block payment |
| **CHAOS-07** | Model Router | All Eligible Models Unavailable | Rule Engine fallback or FAIL CLOSED (`DENY`) | No unvetted model selected |
