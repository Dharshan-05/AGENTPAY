# ATIM Group 7 — Reliability & Resilience Policy

## 1. Non-Negotiable Reliability Invariants
1. **FAIL CLOSED DEFAULT**: If an authoritative component (AGENTGUARD, FRAUDGUARD, HITL, or database state) is unavailable, transaction execution **MUST FAIL CLOSED (`DENY`)**.
2. **FAILURE INJECTION CONTROL**: `ATIM_FAILURE_INJECTION_ENABLED` defaults to `False`. It can only be activated in test suites via explicit environment configuration.
3. **OBSERVABILITY DECOUPLING**: Observability or exporter failure **MUST NEVER** authorize a financial payment or cause unsafe state transitions.
