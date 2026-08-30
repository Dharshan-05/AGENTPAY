# AGENTPAY — 17: Docker & Kubernetes Container Deployment Topology

## 1. Container Deployment Diagram

```mermaid
graph TD
    subgraph Client Tier
        BROWSER[Web Browser / Mobile Approval App]
        AGENT_SDK[AI Agent API Client / LangChain Tool]
    end

    subgraph Edge & Load Balancing
        INGRESS[Nginx Ingress / Cloud Load Balancer (TLS 1.3)]
    end

    subgraph Kubernetes Container Pod Cluster
        POD_GW[API Gateway Pod Replica 1..N]
        POD_CORE[Core Backend Service Pod Replica 1..N]
        POD_ML[FRAUDGUARD Python FastAPI Pod Replica 1..N]
        POD_WORKER[Async Event Worker Pod Replica 1..N]
    end

    subgraph Data Infrastructure Cluster
        DB_PRIMARY[(PostgreSQL Primary Datastore)]
        REDIS_CLUSTER[(Redis Edge Cache Cluster)]
    end

    subgraph External Rails
        RAZORPAY_API[Razorpay API Gateway Sandbox/Live]
    end

    BROWSER & AGENT_SDK --> INGRESS
    INGRESS --> POD_GW
    POD_GW --> POD_CORE & POD_ML
    POD_CORE & POD_ML --> POD_WORKER
    POD_CORE & POD_ML & POD_WORKER --> DB_PRIMARY & REDIS_CLUSTER
    POD_CORE --> RAZORPAY_API
```

---

## 2. Docker Compose Local Stack Topology

* `web`: Next.js 14 Frontend Application (Port 3000).
* `gateway`: API Gateway Router Service (Port 4000).
* `core-backend`: Node.js / Express Core Service (Port 4001).
* `fraudguard`: Python 3.11 / FastAPI Risk Service (Port 5000).
* `postgres`: PostgreSQL 16 DB Container (Port 5432).
* `redis`: Redis 7.2 In-Memory Datastore (Port 6379).
