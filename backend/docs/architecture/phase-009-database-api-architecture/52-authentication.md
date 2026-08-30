# AGENTPAY — 52: Multi-Actor API Authentication (JWT, mTLS, HMAC Key Pairs)

## 1. Authentication Actor Matrix

* **Human Users**: Authenticated via OAuth2 / OIDC JWT Bearer Tokens (`Authorization: Bearer <jwt>`).
* **AI Agents**: Authenticated via HMAC-SHA256 Request Signatures (`X-Agent-Signature`) using pre-enrolled secret keys.
* **Internal Services**: Authenticated via mutual TLS (mTLS) with SPIFFE/SPIRE x509 service certificates.
* **Webhooks**: Authenticated via provider HMAC signatures (`X-Razorpay-Signature`).
