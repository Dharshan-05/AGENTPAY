# AGENTPAY — 63: Refund Execution & Query REST API Contracts

## 1. Refund REST Endpoints

* `POST /api/v1/payments/{payment_id}/refunds`: Initiate full or partial refund (Requires `Idempotency-Key` header).
* `GET /api/v1/refunds/{refund_id}`: Query status of specific refund request.
* `GET /api/v1/payments/{payment_id}/refunds`: List all refunds associated with a payment.
