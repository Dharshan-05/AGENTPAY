# AGENTPAY — 91: Database Write Scaling & Horizontal API Scaling Specs

## 1. Scaling Strategy

* **Stateless API Gateway Layer**: Horizontal pod autoscaling (HPA) in Kubernetes scaling from 3 to 50 replicas based on CPU/RAM thresholds.
* **Database Scaling**: Read replicas handle 100% of non-transactional read queries (`GET /orders`, `GET /merchants`). Primary PostgreSQL node handles strong consistency write transactions (`payments`, `ledger`).
