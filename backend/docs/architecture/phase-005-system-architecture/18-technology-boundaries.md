# AGENTPAY — 18: Production Tech Stack Selection & Justification Matrix

## 1. Production Tech Stack Blueprint

The selected technology stack directly satisfies all performance, reliability, security, and AI explainability requirements defined in Phases 001 through 004.

---

## 2. Technology Selection Matrix

| Subsystem Layer | Selected Technology | Version / Spec | Rationale & Requirements Justification |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | Next.js (React) | v14.2+ (App Router) | Server-side rendering, fast UI updates for Approval Center, Shadcn UI compatibility. |
| **Styling & UI** | Tailwind CSS + Shadcn UI | v3.4+ | Rapid accessible UI component construction for approval cards and XAI decision traces. |
| **Core API Gateway** | Node.js / Express | Node 20 LTS | Fast asynchronous I/O, low-overhead HMAC verification, sub-100ms API pipeline SLA. |
| **AI / Risk Service** | Python / FastAPI | Python 3.11 | High-performance Python async framework for feature extraction and ML model inference. |
| **Risk Scoring Model**| XGBoost Classifier | v2.0+ | Fast CPU-based gradient boosting anomaly classification (< 30ms inference). |
| **XAI Framework** | SHAP (SHapley Additive exPlanations)| v0.44+ | Industry-standard feature attribution tree explainer for transparent risk scoring. |
| **Primary Relational DB**| PostgreSQL | v16+ | ACID compliance, JSONB index queries, row-level locking for atomic daily budget caps. |
| **Database ORM** | Prisma / Drizzle | v5+ | Type-safe SQL migrations, fast query execution, schema generation. |
| **In-Memory Cache & Lock**| Redis | v7.2+ | In-memory key caching, sub-2ms policy lookups, atomic `SETNX` idempotency locking. |
| **Payment Gateway SDK**| Razorpay Node SDK | v2.9+ | Standard integration with Razorpay orders, payments, and HMAC webhook verification. |
| **Containerization** | Docker / Docker Compose | v24+ | Local multi-container zero-dependency hackathon setup & Kubernetes-ready pods. |
| **Telemetry / Logging**| Winston / OpenTelemetry | v3+ | Structured JSON correlation logging (`trace_id`, `intent_id`, `agent_id`). |
