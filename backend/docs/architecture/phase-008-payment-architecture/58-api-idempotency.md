# AGENTPAY — 58: Ingress API Endpoint Idempotency Matrix

## 1. Endpoint Idempotency Matrix

| API Endpoint | Idempotency Header Requirement | Behavior |
| :--- | :--- | :--- |
| `POST /api/v1/payment-intents` | **MANDATORY** (`Idempotency-Key`) | Returns existing intent if key re-used |
| `POST /api/v1/payments/authorize` | **MANDATORY** (`Idempotency-Key`) | Returns existing token if key re-used |
| `POST /api/v1/payments/execute` | **MANDATORY** (`Idempotency-Key`) | Returns existing settlement payload |
| `POST /api/v1/payments/refunds` | **MANDATORY** (`Idempotency-Key`) | Returns existing refund payload |
| `GET /api/v1/payments/{id}` | Forbidden (Read-only GET) | N/A |
