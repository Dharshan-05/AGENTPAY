# AGENTPAY — 65: Ingress Razorpay Webhook Callback API Endpoint Specs

## 1. Webhook Endpoint Contract

* `POST /api/v1/webhooks/razorpay`: Public ingress endpoint receiving Razorpay HTTP POST callbacks.

### Execution Requirements

1. **HMAC Signature Check**: Verifies `X-Razorpay-Signature` against `crypto.createHmac('sha256', secret)`.
2. **Fast Acknowledgment**: Returns HTTP 200 OK within $< 5\text{ ms}$, pushing event payload to Redis queue for background execution.
