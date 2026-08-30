# AGENTPAY — 05: 10 Security Zones & Network Segmentation Matrix

## 1. Security Zone Definitions

```mermaid
graph TD
    Z0[Zone 0: Public Internet] -->|TLS 1.3 | Z1[Zone 1: Edge Gateway]
    Z1 -->|Authenticated HTTP| Z2[Zone 2: Authenticated App Tier]
    Z2 -->|mTLS / Internal API| Z3[Zone 3: Agent Execution Sandbox]
    Z2 -->|gRPC / Internal API| Z4[Zone 4: AGENTGUARD Security Control Plane]
    Z4 -->|Internal Authorization Token| Z5[Zone 5: Payment Orchestrator]
    Z5 -->|TLS 1.3 / HMAC Headers| Z_RAZORPAY[External Razorpay API Rails]
    Z2 & Z4 & Z5 -->|Private DB Driver| Z6[Zone 6: Datastore & Audit Storage]
    Z4 -->|REST API| Z7[Zone 7: AI/ML Inference Container Zone]
    Z2 -->|Authenticated Session| Z8[Zone 8: Security & Risk Console]
    Z1 & Z2 & Z4 & Z5 & Z6 & Z7 & Z8 -->|Internal VPC| Z9[Zone 9: Infrastructure & Management]
```

---

## 2. Zone Communication Matrix

| Source Zone | Destination Zone | Protocol | Purpose | Access Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Zone 0** (Internet) | **Zone 1** (Edge Gateway) | HTTPS / TLS 1.3 | Ingress Client / Agent API Requests | ALLOW (Rate Limited) |
| **Zone 1** (Gateway) | **Zone 2** (App Tier) | HTTP / Internal API | Ingress Request Forwarding | ALLOW (Authenticated Only) |
| **Zone 2** (App Tier) | **Zone 4** (AGENTGUARD) | gRPC / Internal REST| Policy Evaluation Trigger | ALLOW (Internal Network Only) |
| **Zone 4** (AGENTGUARD) | **Zone 5** (Payment) | Internal Token | Authorized Payment Execution Dispatch| ALLOW (Valid Auth Token Only) |
| **Zone 3** (Agent Exec) | **Zone 5** (Payment) | Direct HTTP | Direct Payment Execution Attempt | **DENY ALL** (Must route via Zone 4) |
| **Zone 0** (Internet) | **Zone 6** (Datastores) | Any | Direct Database Connection | **DENY ALL** |
