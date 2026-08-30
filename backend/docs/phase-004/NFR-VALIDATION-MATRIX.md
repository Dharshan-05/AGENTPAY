# AGENTPAY — Master NFR Validation Matrix

## 1. Master Validation Matrix Table

| NFR ID | Category | Priority | Target Horizon | Metric | Target Value | Measurement Method | Source FR | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-PERF-001**| Performance | P0 | MVP TARGET | Latency ($p_{99}$) | $\le 100\text{ ms}$ | Locust Load Test | `FR-INTENT-001` | NOT YET MEASURED |
| **NFR-PERF-002**| Performance | P0 | MVP TARGET | Latency ($p_{99}$) | $\le 15\text{ ms}$ | Microbenchmark | `FR-AGD-001` | NOT YET MEASURED |
| **NFR-PERF-003**| Performance | P0 | MVP TARGET | Latency ($p_{99}$) | $\le 20\text{ ms}$ | Server Timer | `FR-FRD-001` | NOT YET MEASURED |
| **NFR-PERF-004**| AI/ML | P0 | MVP TARGET | Latency ($p_{99}$) | $\le 30\text{ ms}$ | Inference Timer | `FR-FRD-002` | NOT YET MEASURED |
| **NFR-PERF-005**| XAI | P0 | MVP TARGET | Latency ($p_{99}$) | $\le 10\text{ ms}$ | Text Timer | `FR-XAI-002` | NOT YET MEASURED |
| **NFR-AVAIL-001**| Availability | P0 | MVP TARGET | % Uptime | $\ge 99.9\%$ | Ping Probe | `FR-AUTH-003` | NOT YET MEASURED |
| **NFR-REL-001** | Payment Rel | P0 | MVP TARGET | Duplicate Rate | $0$ duplicates | Parallel Load Test| `FR-INTENT-002` | NOT YET MEASURED |
| **NFR-REL-002** | Resilience | P0 | MVP TARGET | Fail-Safe Rate | $100\%$ Default Block| Fault Injection | `FR-ERR-001` | NOT YET MEASURED |
| **NFR-SCALE-001**| Scalability | P1 | PROTOTYPE | Throughput | $\ge 500\text{ req/sec}$ | Stress Test | `FR-INTENT-001` | NOT YET MEASURED |
| **NFR-SEC-001**  | Security | P0 | MVP TARGET | Protocol | TLS 1.3 Mandated | SSL Labs Scan | `FR-AUTH-003` | NOT YET MEASURED |
| **NFR-SEC-002**  | Security | P0 | MVP TARGET | Hash Parameter | Argon2id ($m=64\text{MB}$)| DB Code Audit | `FR-AGENT-002` | DEFINED |
| **NFR-SEC-003**  | Agent Sec | P0 | MVP TARGET | Purge Speed | $< 10\text{ ms}$ | Revocation Test | `FR-AGENT-003` | NOT YET MEASURED |
| **NFR-SEC-004**  | Operational | P0 | MVP TARGET | Propagation | $< 100\text{ ms}$ | Kill Switch Test| `FR-EMG-001` | NOT YET MEASURED |
| **NFR-PRIV-001** | Privacy | P0 | MVP TARGET | Isolation | Zero Card/PIN in AI| Payload Scanner | `FR-PAY-001` | DEFINED |
| **NFR-INT-001**  | Integrity | P0 | MVP TARGET | Hash Chain | $100\%$ Valid Chain | Block Hash Verifier| `FR-AUD-001` | NOT YET MEASURED |
| **NFR-CONS-001** | Consistency | P0 | MVP TARGET | Overrun Rate | Zero budget overrun | Concurrent Lock | `FR-POLICY-001` | NOT YET MEASURED |
| **NFR-OBS-001**  | Observability | P0 | MVP TARGET | JSON Schema | $100\%$ Compliance | Schema Validator | `FR-MON-001` | DEFINED |
| **NFR-MNT-001**  | Maintainability| P1 | MVP TARGET | Test Coverage | $\ge 80.0\%$ Coverage | Jest Coverage | All FRs | NOT YET MEASURED |
| **NFR-TST-001**  | Testability | P0 | MVP TARGET | Offline Suite | $100\%$ Offline Suite | Offline Integration| `FR-PAY-001` | DEFINED |
| **NFR-USE-001**  | Usability | P0 | MVP TARGET | Action Depth | $\le 2$ Clicks | UI Step Counter | `FR-APP-002` | DEFINED |
| **NFR-ACC-001**  | Accessibility | P1 | PROTOTYPE | Compliance | WCAG 2.1 Level AA | Axe-core Audit | `FR-DSH-001` | NOT YET MEASURED |
| **NFR-AML-001**  | AI/ML | P1 | PROTOTYPE | FPR Rate | $< 2.0\%$ FPR | Model Validation | `FR-FRD-002` | NOT YET MEASURED |
| **NFR-AML-002**  | AI/ML | P0 | MVP TARGET | Timeout | $100\text{ ms}$ Timeout | Fault Injection | `FR-FRD-002` | NOT YET MEASURED |
| **NFR-XAI-001**  | XAI | P0 | MVP TARGET | Completeness | $100\%$ Trace Coverage| Schema Audit | `FR-XAI-001` | NOT YET MEASURED |
| **NFR-PAY-001**  | Payment Rel | P0 | MVP TARGET | Gateway Timeout| $5,000\text{ ms}$ SLA | Gateway Simulator | `FR-PAY-001` | NOT YET MEASURED |
| **NFR-BKP-001**  | Recovery | P2 | FUTURE PROD | RPO / RTO | RPO $< 1\text{h}$, RTO $< 15\text{m}$| DB Restore Drill | `FR-AUD-001` | DEFERRED |
| **NFR-DR-001**   | Recovery | P0 | MVP TARGET | Rebuild Speed | $< 60\text{ seconds}$ | Redis Flush Test | `FR-AGD-001` | NOT YET MEASURED |
| **NFR-DEP-001**  | Deployment | P0 | MVP TARGET | Drain Window | 15s Grace Window | Container Stop | `FR-PAY-001` | DEFINED |
| **NFR-OPS-001**  | Operational | P0 | MVP TARGET | Isolation | 3 Retries $\rightarrow$ DLQ | DLQ Router Test | `FR-ERR-001` | DEFINED |
| **NFR-RES-001**  | Resources | P1 | MVP TARGET | Container RAM | $\le 512\text{ MB}$ API RAM| Docker Stats | All FRs | DEFINED |
| **NFR-CMP-001**  | Compatibility | P1 | MVP TARGET | OpenAPI | $100\%$ OpenAPI 3.0 | Schema Validator | `FR-AUTH-003` | DEFINED |
