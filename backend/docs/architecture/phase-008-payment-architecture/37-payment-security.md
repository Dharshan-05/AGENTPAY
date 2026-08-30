# AGENTPAY — 37: Phase 006 Security Controls Integration

## 1. Security Controls Integration Matrix

* **Zero Trust Ingress**: 9-step continuous verification on all payment API requests.
* **Cryptographic HMAC Agent Signing**: HMAC-SHA256 headers (`X-Agent-Signature`) required for agent payment intent proposals.
* **PostgreSQL RLS Multi-Tenancy**: Database queries enforce `tenant_id` context filtering.
* **Fail-Closed Gateways**: Provider timeouts and risk service crashes fail closed to `BLOCK` or `REVIEW`.
