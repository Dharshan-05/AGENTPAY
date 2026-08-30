# AGENTPAY — NFR Traceability Matrix

## 1. Traceability Model

This document establishes bidirectional traceability from core problem domains and functional requirements down to NFR specifications and validation methods.

$$\text{Core Problem} \longrightarrow \text{Functional Requirement} \longrightarrow \text{NFR ID} \longrightarrow \text{Acceptance Criteria} \longrightarrow \text{Validation Method}$$

---

## 2. Master NFR Traceability Matrix Table

| Core Problem | Source FR ID | NFR ID | NFR Category | Acceptance Criteria | Validation Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent Speed** | `FR-INTENT-001` | `NFR-PERF-001` | Performance | $p_{99} \le 100\text{ ms}$ | Locust Load Test |
| **Policy Speed** | `FR-AGD-001` | `NFR-PERF-002` | Performance | $p_{99} \le 15\text{ ms}$ | Microbenchmark Timer |
| **Feature Extraction**| `FR-FRD-001` | `NFR-PERF-003` | Performance | $p_{99} \le 20\text{ ms}$ | Execution Timer |
| **AI Inference** | `FR-FRD-002` | `NFR-PERF-004` | AI/ML | $p_{99} \le 30\text{ ms}$ | Container SLA Monitor |
| **XAI Latency** | `FR-XAI-002` | `NFR-PERF-005` | XAI | $p_{99} \le 10\text{ ms}$ | Text Synthesis Timer |
| **Uptime** | `FR-AUTH-003` | `NFR-AVAIL-001` | Availability | $\ge 99.9\%$ Uptime | Synthetic Ping Probe |
| **Double-Spending** | `FR-INTENT-002` | `NFR-REL-001` | Reliability | $0$ duplicates | Parallel Duplicate Test |
| **Fail-Safe Safety** | `FR-ERR-001` | `NFR-REL-002` | Resilience | $100\%$ Default Block | Fault Injection Test |
| **Throughput** | `FR-INTENT-001` | `NFR-SCALE-001` | Scalability | $\ge 500\text{ req/sec}$ | Distributed Stress Test |
| **Transport Sec** | `FR-AUTH-003` | `NFR-SEC-001` | Security | TLS 1.3 Mandated | SSL Labs Scan |
| **Key Hashing** | `FR-AGENT-002` | `NFR-SEC-002` | Security | Argon2id Hash Prefix | DB Hash Inspection |
| **Revocation** | `FR-AGENT-003` | `NFR-SEC-003` | Agent Security | $< 10\text{ ms}$ Cache Purge | Revocation Latency Test |
| **Kill Switch** | `FR-EMG-001` | `NFR-SEC-004` | Operational Sec| $< 100\text{ ms}$ Propagation| Emergency Stop Test |
| **Privacy Isolation**| `FR-PAY-001` | `NFR-PRIV-001` | Privacy | Zero Card/PIN in AI | Payload Scanner Audit |
| **Audit Integrity** | `FR-AUD-001` | `NFR-INT-001` | Data Integrity | $100\%$ Hash Chain Pass| Cryptographic Verifier |
| **Budget Race** | `FR-POLICY-001` | `NFR-CONS-001` | Consistency | Zero budget overruns | Concurrent Lock Test |
| **Observability** | `FR-MON-001` | `NFR-OBS-001` | Observability | $100\%$ JSON Log Schema| Log Schema Validator |
| **Test Coverage** | All FRs | `NFR-MNT-001` | Maintainability | $\ge 80.0\%$ Coverage | Jest Coverage Report |
