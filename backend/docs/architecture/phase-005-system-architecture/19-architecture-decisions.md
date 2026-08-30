# AGENTPAY — 19: Master Architecture Decision Records (ADR-001 to ADR-012)

## 1. Overview

This document formalizes twelve Architecture Decision Records (ADR-001 through ADR-012) detailing architectural choices, alternatives considered, trade-offs, and consequences.

---

## 2. Architecture Decision Records

### ADR-001: Modular Microservices Architecture
* **Context**: System must separate fast API gateway execution, policy checks, ML risk scoring, and payment rails.
* **Decision**: Adopt a modular microservices architecture decomposed into Gateway, Core Backend, Python Risk Service, and Async Workers.
* **Alternatives**: Monolithic single-service application.
* **Reasoning**: Decouples heavy Python ML dependencies from lightweight API routing; allows independent auto-scaling.
* **Consequences**: Requires structured inter-service communication and distributed correlation logging.

---

### ADR-002: Payment Orchestrator Boundary Decoupling
* **Context**: Direct coupling between AI agents and Razorpay API creates vendor lock-in and security risks.
* **Decision**: Implement an abstract `IPaymentAdapter` interface decoupling internal intent logic from specific gateways.
* **Alternatives**: Direct Razorpay API calls embedded in agent tools.
* **Reasoning**: Protects core pipeline; allows instant swapping between Gateway Simulator and Razorpay Sandbox/Live rails.
* **Consequences**: Requires translation adapters for payment gateway payloads.

---

### ADR-003: AGENTGUARD Architectural Isolation
* **Context**: Autonomous AI AGENT logic must not control financial authorization gates.
* **Decision**: AGENTGUARD operates as an independent security control plane capable of blocking transactions regardless of agent decisions.
* **Alternatives**: Agent internal self-checking prompt rules.
* **Reasoning**: Self-checking prompt rules are vulnerable to prompt injection attacks; external policy gates guarantee security.
* **Consequences**: Introduces sub-15ms inter-service policy evaluation network call.

---

### ADR-004: PostgreSQL Primary Relational Database Selection
* **Context**: Need primary datastore supporting atomic transaction state transitions, JSONB metadata, and immutable block hash chains.
* **Decision**: Select PostgreSQL 16 as the primary datastore.
* **Alternatives**: MongoDB, SQLite, MySQL.
* **Reasoning**: Row-level pessimistic locking (`SELECT FOR UPDATE`) prevents concurrent daily budget overruns.
* **Consequences**: Requires Docker container setup during local development.

---

### ADR-005: Redis Edge Caching & Idempotency Locking
* **Context**: High-speed policy lookups (< 2ms) and double-spend prevention require fast in-memory key storage.
* **Decision**: Deploy Redis 7.2 for policy caching, rate limiting, and atomic `SETNX` idempotency locking.
* **Alternatives**: Memcached, DB-only locking.
* **Reasoning**: Redis provides sub-millisecond key lookups and distributed locking capabilities.
* **Consequences**: Requires cache invalidation triggers on policy updates.

---

### ADR-006: Asynchronous Worker Event Processing
* **Context**: Heavy audit hashing, notification alerts, and webhook reconciliation must not block synchronous 100ms intent SLA.
* **Decision**: Route background tasks asynchronously via Redis Pub/Sub worker queues.
* **Alternatives**: Synchronous inline processing.
* **Reasoning**: Preserves sub-100ms API latency by offloading non-critical tasks.
* **Consequences**: Eventual consistency for non-critical telemetry streams.

---

### ADR-007: Python FastAPI XGBoost ML Inference Architecture
* **Context**: FRAUDGUARD requires fast machine learning anomaly classification and SHAP feature attribution synthesis.
* **Decision**: Deploy Python 3.11 with FastAPI running XGBoost and SHAP explainers in an isolated container service.
* **Alternatives**: Node.js ML bindings.
* **Reasoning**: Python provides native, highly optimized C++ bindings for XGBoost and SHAP.
* **Consequences**: Inter-service REST call from Node.js core backend to Python risk container.

---

### ADR-008: RESTful API Versioning Protocol (`/api/v1/`)
* **Context**: Public API gateway must preserve backward compatibility as agent capabilities evolve.
* **Decision**: Enforce URI path versioning under `/api/v1/` namespace.
* **Alternatives**: Header-based versioning.
* **Reasoning**: URI path versioning is transparent and widely supported across all AI agent SDKs.
* **Consequences**: Route controllers must maintain version namespaces.

---

### ADR-009: Row-Level Security (RLS) Multi-Tenancy Isolation
* **Context**: Multi-tenant architecture requires absolute data isolation between user accounts and merchants.
* **Decision**: Implement PostgreSQL Row-Level Security (RLS) policies scoped by `tenant_id`.
* **Alternatives**: Separate database per tenant.
* **Reasoning**: RLS provides hardware-level data isolation without the overhead of managing thousands of databases.
* **Consequences**: All database queries must inject `tenant_id` context.

---

### ADR-010: Idempotent Payment Intent Processing
* **Context**: Network retries or parallel agent calls must never execute duplicate financial payments.
* **Decision**: Mandate 24-hour Redis idempotency locking based on agent-provided `idempotency_key` headers.
* **Alternatives**: Non-idempotent retry processing.
* **Reasoning**: Guarantees zero duplicate payment clearing under network retries.
* **Consequences**: Agents must generate unique UUID v4 idempotency keys.

---

### ADR-011: Human-in-the-Loop Approval Center Architecture
* **Context**: High-value or medium-risk autonomous intents must permit human intervention without breaking pipeline state.
* **Decision**: Intents with decision `REVIEW` transition to `PENDING_APPROVAL` with a 15-minute TTL, pushing real-time alerts to the Approval Center UI.
* **Alternatives**: Immediate rejection of all high-value intents.
* **Reasoning**: Balances safe autonomy with human control, maximizing transaction completion rates.
* **Consequences**: State machine must manage 15-minute expiration timeouts.

---

### ADR-012: OpenTelemetry & Structured JSON Observability
* **Context**: Distributed microservice transactions require end-to-end trace correlation and structured debugging.
* **Decision**: Standardize on structured JSON logging with OpenTelemetry W3C `trace_id` headers across all services.
* **Alternatives**: Unstructured plain text logging.
* **Reasoning**: Enables instant cross-service transaction tracing and automated Grafana dashboard ingestion.
* **Consequences**: Logging libraries must enforce structured JSON schemas.
