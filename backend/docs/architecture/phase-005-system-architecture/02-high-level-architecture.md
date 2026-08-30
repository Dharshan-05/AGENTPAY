# AGENTPAY — 02: High-Level System Architecture (9 Logical Layers)

## 1. Architectural Blueprint

AGENTPAY is architected across nine logical layers, providing clean separation of concerns between user experience, edge security, policy enforcement, AI risk intelligence, payment orchestration, and immutable auditability.

```mermaid
graph TB
    subgraph Layer 1: Experience Layer
        UI_USER[Web Dashboard & Wallet UI]
        UI_APPROVAL[Approval Center UI]
        UI_SECURITY[Security & Risk Console]
        UI_MERCHANT[Merchant Verification Portal]
    end

    subgraph Layer 2: API & Edge Gateway Layer
        API_GW[API Gateway Router]
        AUTH_JWT[JWT Session Validator]
        AUTH_HMAC[HMAC Request Authenticator]
        RATE_LIMIT[Redis Rate Limiter]
        IDEMPOTENCY[Redis Idempotency Manager]
    end

    subgraph Layer 3: Agent Orchestration Layer
        REGISTRY[Agent Identity Registry]
        SCHEDULER[Agent Task Manager]
        POLICY_EVAL[Policy Evaluator]
        APPROVE_MGR[Approval Queue Manager]
    end

    subgraph Layer 4: AGENTGUARD Trust & Security Layer
        POLICY_ENGINE[AGENTGUARD Policy Engine]
        TRUST_ENGINE[Multi-Factor Trust Engine]
        BEHAVIOR_ENGINE[Behavioral Anomaly Detector]
        DECISION_ENGINE[Authorization Decision Engine]
    end

    subgraph Layer 5: Payment Orchestration Layer
        PAY_ORCH[Payment Intent Pipeline]
        STATE_ENGINE[Transaction State Machine]
        RAZORPAY_ADAPTER[Razorpay Integration Adapter]
        SIMULATOR_ADAPTER[Payment Gateway Simulator]
    end

    subgraph Layer 6: Data & Persistence Layer
        DB_PG[(PostgreSQL Primary DB)]
        CACHE_REDIS[(Redis Edge Cache & Lock Store)]
        AUDIT_STORE[(Tamper-Evident SHA-256 Audit Log)]
    end

    subgraph Layer 7: AI / ML & XAI Layer
        MODEL_FRAUD[FRAUDGUARD XGBoost Risk Model]
        FEATURE_STORE[12-D Feature Processing Engine]
        XAI_ENGINE[SHAP Feature Attribution & Text Synthesis]
    end

    subgraph Layer 8: Asynchronous Processing Layer
        EVENT_BUS[Redis Pub/Sub & Worker Queue]
        WORKER_WEBHOOK[Webhook Processing Worker]
        WORKER_AUDIT[Audit Log Archiver]
        WORKER_DLQ[Dead-Letter Queue Worker]
    end

    subgraph Layer 9: Observability Layer
        PROMETHEUS[Prometheus Metrics Collector]
        GRAFANA[Grafana Telemetry Dashboards]
        LOGGER[JSON Correlation Logger]
    end

    UI_USER & UI_APPROVAL & UI_SECURITY -->|HTTPS TLS 1.3| API_GW
    API_GW --> AUTH_JWT & AUTH_HMAC & RATE_LIMIT & IDEMPOTENCY
    AUTH_HMAC --> REGISTRY
    API_GW --> SCHEDULER
    SCHEDULER --> POLICY_EVAL
    POLICY_EVAL --> POLICY_ENGINE
    POLICY_ENGINE --> TRUST_ENGINE & BEHAVIOR_ENGINE & MODEL_FRAUD
    MODEL_FRAUD --> FEATURE_STORE & XAI_ENGINE
    XAI_ENGINE --> DECISION_ENGINE
    DECISION_ENGINE -->|ALLOW / Approved| PAY_ORCH
    DECISION_ENGINE -->|REVIEW| APPROVE_MGR
    APPROVE_MGR --> UI_APPROVAL
    PAY_ORCH --> STATE_ENGINE
    STATE_ENGINE --> RAZORPAY_ADAPTER & SIMULATOR_ADAPTER
    RAZORPAY_ADAPTER --> DB_PG & CACHE_REDIS
    PAY_ORCH --> EVENT_BUS
    EVENT_BUS --> WORKER_WEBHOOK & WORKER_AUDIT & WORKER_DLQ
    WORKER_AUDIT --> AUDIT_STORE
    API_GW & PAY_ORCH & POLICY_ENGINE --> PROMETHEUS & LOGGER
```

---

## 2. Operating Modes

### Mode 1: Human-Assisted Commerce
User initiates intent via web console; system executes policy and risk checks; if compliant, payment is routed to Razorpay checkout rails with human approval verification.

### Mode 2: Autonomous Agent Commerce
Autonomous AI AGENT initiates intent via API using HMAC credentials. AGENTGUARD evaluates 6-stage policy rules; FRAUDGUARD computes risk score (0-100) and XAI trace. If safe ($\le$ auto-approval limit and low risk), payment executes autonomously without human friction. If uncertain or high risk, payment is held in `PENDING_APPROVAL` status and pushed to the human user's Approval Center.
