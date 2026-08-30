# AGENTPAY — 08: Razorpay API Gateway Adapter Specifications

## 1. Razorpay Adapter Mapping

`RazorpayAdapter` implements `IPaymentProvider`, translating internal domain entities into Razorpay API endpoints:

| Internal Domain Operation | Razorpay API Endpoint | Adapter Execution |
| :--- | :--- | :--- |
| `createOrder()` | `POST /v1/orders` | Maps `amount`, `currency`, `receipt = order_id` |
| `executePayment()` | `POST /v1/payments/create/json` | Dispatches settlement payload |
| `getPayment()` | `GET /v1/payments/{id}` | Queries authoritative settlement status |
| `refundPayment()` | `POST /v1/payments/{id}/refund` | Maps `amount`, `speed = normal/optimum` |
| `verifyWebhook()` | HMAC-SHA256 Checksum | `crypto.createHmac('sha256', secret)` |
