# AGENTPAY — 03: Microservices & Component Structural Specifications

## 1. Microservice Decomposition

AGENTPAY decomposes system responsibilities into six core microservices communicating via HTTP/gRPC and Redis Pub/Sub event queues.

```mermaid
graph TD
    subgraph Microservice Boundaries
        SVC_GATEWAY[API Gateway Container]
        SVC_AGENT[Agent Orchestrator Service]
        SVC_GUARD[AGENTGUARD Security Service]
        SVC_FRAUD[FRAUDGUARD Risk Service (Python FastAPI)]
        SVC_PAYMENT[Payment Processing Service]
        SVC_WORKER[Async Worker Service]
    end

    subgraph Internal Subsystems
        HMAC_VERIFIER[HMAC Signature Verifier]
        POLICY_ENGINE[6-Stage Policy Pipeline]
        FEATURE_CALC[12-D Feature Processing Engine]
        XGBOOST_MODEL[XGBoost Anomaly Scoring Model]
        SHAP_EXPLAINER[SHAP Attribution Synthesizer]
        STATE_MACHINE[14-State Transaction Machine]
        RAZORPAY_CLIENT[Razorpay API Gateway Adapter]
    end

    SVC_GATEWAY --> HMAC_VERIFIER
    HMAC_VERIFIER --> SVC_AGENT
    SVC_AGENT --> SVC_GUARD
    SVC_GUARD --> POLICY_ENGINE
    POLICY_ENGINE --> SVC_FRAUD
    SVC_FRAUD --> FEATURE_CALC
    FEATURE_CALC --> XGBOOST_MODEL
    XGBOOST_MODEL --> SHAP_EXPLAINER
    SHAP_EXPLAINER --> SVC_GUARD
    SVC_GUARD -->|Authorized Payload| SVC_PAYMENT
    SVC_PAYMENT --> STATE_MACHINE
    STATE_MACHINE --> RAZORPAY_CLIENT
    SVC_PAYMENT --> SVC_WORKER
```

---

## 2. Component Specifications

### 2.1 API Gateway Container (`SVC_GATEWAY`)
* **Role**: Ingress routing, TLS termination, rate limiting, HMAC signature verification, JWT session decoding, idempotency key locking.
* **Tech**: Node.js / Express / Redis Edge Cache.

### 2.2 AGENTGUARD Security Service (`SVC_GUARD`)
* **Role**: 6-Stage Policy rule evaluation, Emergency Stop state checks, decision aggregation (`ALLOW`, `REVIEW`, `CHALLENGE`, `BLOCK`).
* **Tech**: Node.js / TypeScript / Redis In-Memory Cache.

### 2.3 FRAUDGUARD AI Risk Service (`SVC_FRAUD`)
* **Role**: 12-Dimensional feature extraction, XGBoost risk model scoring, SHAP feature attribution calculation, natural text explanation generation.
* **Tech**: Python 3.11 / FastAPI / XGBoost / SHAP / PyTorch.

### 2.4 Payment Processing Service (`SVC_PAYMENT`)
* **Role**: 14-State transaction state machine execution, Razorpay integration adapter management, payment simulator settlement, reconciliation logging.
* **Tech**: Node.js / TypeScript / Razorpay Node SDK.
