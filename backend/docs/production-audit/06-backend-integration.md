# 06 — Backend Integration & Server Endpoint Inventory

## 1. Backend Microservices Inventory
* **Core API Gateway (`apps/api`)**: Express Node.js application, port 4000.
* **AGENTGUARD Control Plane (`apps/agentguard`)**: Express Node.js application.
* **Agent AI Runtime (`apps/agent-runtime`)**: Python FastAPI + XGBoost application, port 8000.
* **Outbox Worker (`apps/worker`)**: Transactional outbox event listener.

## 2. Endpoint Parity Matrix
All 13 frontend data requirements match the REST endpoint paths specified in Phase 009 (`docs/architecture/phase-009-database-api-architecture/`).
