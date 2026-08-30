# AGENTPAY — 27: `apps/agentguard` Policy & Security Control Plane Specs

## 1. AGENTGUARD Microservice Blueprint

* Exposes `POST /api/v1/agentguard/evaluate`.
* Integrates 6-stage policy verification engine, FRAUDGUARD ML risk assessment, and cryptographic token signing.
