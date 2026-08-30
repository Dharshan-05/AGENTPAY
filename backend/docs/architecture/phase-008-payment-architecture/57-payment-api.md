# AGENTPAY — 57: RESTful API Endpoints (`/api/v1/payments/...`)

## 1. Primary Payment Endpoints

* `POST /api/v1/payment-intents`: Create proposed payment intent payload.
* `POST /api/v1/payments/authorize`: Issue cryptographic payment authorization token.
* `POST /api/v1/payments/execute`: Execute payment settlement through Razorpay adapter.
* `GET /api/v1/payments/{payment_id}`: Query authoritative payment status.
* `POST /api/v1/payments/{payment_id}/refunds`: Initiate full/partial refund.
* `POST /api/v1/webhooks/razorpay`: Ingress endpoint for Razorpay webhook callbacks.
