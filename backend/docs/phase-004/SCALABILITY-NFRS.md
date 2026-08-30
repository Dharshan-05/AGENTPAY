# AGENTPAY — Scalability Non-Functional Requirements

## 1. Overview

Scalability requirements define baseline workloads, growth expectations, stress targets, and horizontal auto-scaling triggers across API gateways, evaluation pipelines, and datastores.

---

## 2. Requirement Baseline

### NFR-SCALE-001: Concurrent Intent Request Throughput
* **NFR ID**: `NFR-SCALE-001`
* **Title**: Concurrent Intent Request Processing Throughput
* **Source FR**: `FR-INTENT-001`
* **Priority**: P1 | **Target Horizon**: PROTOTYPE TARGET
* **Category**: Scalability
* **Requirement**: The API gateway and evaluation pipeline shall process a sustained load of 500 intent requests/second without exceeding the 100ms $p_{99}$ latency SLA.
* **Rationale**: Multi-agent commercial ecosystems require scaling throughput to handle burst payment events.
* **Metric & Targets**:
  * MVP Baseline Target: $50\text{ req/sec}$
  * Prototype Stress Target: $500\text{ req/sec}$
  * Future Production Target: $5,000\text{ req/sec}$
* **Measurement Method**: Distributed load testing using Locust across multi-threaded worker nodes.
* **Acceptance Criteria**: Pipeline maintains $\ge 500\text{ req/sec}$ throughput for 15 minutes with $0\%$ error rate and $p_{99} \le 100\text{ ms}$.
* **Dependencies**: Redis cluster & DB connection pooling.

---

### NFR-SCALE-002: Horizontal Stateless API Scaling
* **NFR ID**: `NFR-SCALE-002`
* **Title**: Horizontal Stateless Worker Scaling Trigger
* **Source FR**: `FR-AUTH-003`
* **Priority**: P1 | **Target Horizon**: PROTOTYPE TARGET
* **Category**: Scalability
* **Requirement**: API Gateway and evaluation worker nodes shall remain strictly stateless, supporting auto-scaling based on CPU utilization ($\ge 70\%$) or queue depth.
* **Rationale**: Stateless node design enables seamless container auto-scaling during high-traffic surges.
* **Metric & Target**: Auto-scale trigger at CPU $\ge 70\%$ for 60s; scale-up time $< 30\text{ seconds}$.
* **Measurement Method**: Container orchestration auto-scaling stress test.
* **Acceptance Criteria**: Worker replica count automatically scales from 2 to 6 containers during load surge.
* **Dependencies**: Stateless JWT & HMAC session architecture.
