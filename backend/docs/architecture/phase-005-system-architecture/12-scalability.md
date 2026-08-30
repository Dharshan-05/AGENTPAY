# AGENTPAY — 12: Horizontal Stateless Worker & Datastore Scaling Strategy

## 1. Scalability Architecture

AGENTPAY achieves high throughput by keeping worker processes stateless and scaling datastores independently.

---

## 2. Component Scaling Classification

| Component | State Classification | Scaling Strategy | Scaling Bottleneck / Trigger |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Stateless | Horizontal Pod Autoscaling (HPA) | CPU $\ge 70\%$ for 60s |
| **AGENTGUARD Engine** | Stateless (Redis Cached)| Horizontal Replica Pods | Memory / CPU $\ge 70\%$ |
| **FRAUDGUARD AI Service**| Stateless Inference | GPU/CPU Multi-Worker Pods | Inference Queue Depth $\ge 50$ |
| **Payment Service** | Stateless Orchestration | Horizontal Worker Scaling | Inflight Intent Count |
| **Redis Cache** | In-Memory Stateful | Redis Cluster Sharding | Memory Max Limit ($80\%$) |
| **PostgreSQL DB** | Relational Stateful | Primary-Replica Read Scaling | Connection Pool / IOPS |

---

## 3. Workload Horizons

* **MVP Target**: 50 req/sec | 2 API Gateway Replicas | Single PostgreSQL instance.
* **Prototype Stress Target**: 500 req/sec | 6 API Gateway Replicas | Redis Primary-Replica.
* **Future Production Target**: 5,000 req/sec | Kubernetes Auto-scaled Cluster | PostgreSQL Sharded Cluster.
