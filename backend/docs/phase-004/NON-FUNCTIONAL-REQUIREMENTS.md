# AGENTPAY — Master Non-Functional Requirements Specification

## 1. Executive Summary

This document establishes the master Non-Functional Requirements (NFR) specification for **AGENTPAY**, **AGENTGUARD**, and **FRAUDGUARD**. Building upon the functional behavior defined in Phase 003, this phase specifies quantitative, measurable, testable, and implementation-independent quality attributes across 25 non-functional categories.

---

## 2. NFR Classification & Target Horizon Model

Every NFR in this specification is explicitly assigned a **Target Classification** to prevent non-verifiable or fabricated benchmark claims:

1. **MVP TARGET**: Measurable SLA required for the hackathon MVP demonstration.
2. **PROTOTYPE TARGET**: Performance baseline for single-region prototype stress testing.
3. **FUTURE PRODUCTION TARGET**: Long-term enterprise production engineering SLA.

---

## 3. Master NFR Inventory Table

| NFR ID | Title | Category | Target Value | Priority | Target Horizon | Source FR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-PERF-001**| Intent API Latency | Performance | $\le 100\text{ ms}$ ($p_{99}$) | P0 | MVP TARGET | `FR-INTENT-001` |
| **NFR-PERF-002**| AGENTGUARD Engine Latency| Performance | $\le 15\text{ ms}$ ($p_{99}$) | P0 | MVP TARGET | `FR-AGD-001` |
| **NFR-PERF-003**| FRAUDGUARD Feature Latency| Performance | $\le 20\text{ ms}$ ($p_{99}$) | P0 | MVP TARGET | `FR-FRD-001` |
| **NFR-PERF-004**| FRAUDGUARD Inference Latency| AI/ML | $\le 30\text{ ms}$ ($p_{99}$) | P0 | MVP TARGET | `FR-FRD-002` |
| **NFR-PERF-005**| XAI Text Synthesis Latency| XAI | $\le 10\text{ ms}$ ($p_{99}$) | P0 | MVP TARGET | `FR-XAI-002` |
| **NFR-AVAIL-001**| Gateway API Availability | Availability | $99.9\%$ Uptime | P0 | MVP TARGET | `FR-AUTH-003` |
| **NFR-REL-001** | Zero Double-Spend Guarantee| Payment Rel | $100.0\%$ (Zero duplicates)| P0 | MVP TARGET | `FR-INTENT-002` |
| **NFR-REL-002** | Fail-Safe Default on Error| Resilience | $100.0\%$ Default Block | P0 | MVP TARGET | `FR-ERR-001` |
| **NFR-SCALE-001**| Concurrent Agent Throughput| Scalability | $\ge 500\text{ req/sec}$ | P1 | PROTOTYPE TARGET| `FR-INTENT-001` |
| **NFR-SEC-001**  | TLS 1.3 Encryption | Security | $100\%$ TLS 1.3 Transport | P0 | MVP TARGET | `FR-AUTH-003` |
| **NFR-SEC-002**  | Argon2id Key Hashing | Security | $m=64\text{MB}, t=3, p=4$ | P0 | MVP TARGET | `FR-AGENT-002` |
| **NFR-SEC-003**  | Revocation Propagation Speed| Agent Sec | $< 10\text{ ms}$ Cache Purge | P0 | MVP TARGET | `FR-AGENT-003` |
| **NFR-SEC-004**  | Emergency Stop Propagation| Operational Sec| $< 100\text{ ms}$ Propagation| P0 | MVP TARGET | `FR-EMG-001` |
| **NFR-PRIV-001** | Zero Raw Credential Logging| Privacy | Zero raw banking tokens | P0 | MVP TARGET | `FR-PAY-001` |
| **NFR-INT-001**  | SHA-256 Audit Block Chain| Data Integrity | $100\%$ Verified Hash Chain| P0 | MVP TARGET | `FR-AUD-001` |
| **NFR-CONS-001** | Atomic Daily Budget Locking| Consistency | $100\%$ Serialized Locks | P0 | MVP TARGET | `FR-POLICY-001` |
| **NFR-OBS-001**  | Structured JSON Telemetry | Observability | $100\%$ JSON Logs | P0 | MVP TARGET | `FR-MON-001` |
| **NFR-AML-001**  | False Positive Rate | AI/ML | $< 2.0\%$ False Positives | P1 | PROTOTYPE TARGET| `FR-FRD-002` |
| **NFR-XAI-001**  | Explanation Trace Completeness| XAI | $100\%$ Trace Coverage | P0 | MVP TARGET | `FR-XAI-001` |
| **NFR-PAY-001**  | Gateway Timeout SLA | Payment Rel | $5,000\text{ ms}$ Hard SLA | P0 | MVP TARGET | `FR-PAY-001` |
| **NFR-BKP-001**  | RPO / RTO Target | Recovery | RPO $< 1\text{h}$, RTO $< 15\text{m}$| P2 | FUTURE PROD | `FR-AUD-001` |
