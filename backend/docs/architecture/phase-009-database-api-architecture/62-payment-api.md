# AGENTPAY — 62: Core Payment Execution REST API Endpoints Specification

## 1. Settlement Endpoints

* `POST /api/v1/payments/execute`: Execute settlement payload via Razorpay adapter (Requires `Authorization: Bearer <auth_token>` & `Idempotency-Key` headers).
* `GET /api/v1/payments/{payment_id}`: Query authoritative settlement status.
* `GET /api/v1/payments`: Search tenant payments with status filtering.
