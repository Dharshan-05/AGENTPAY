# AGENTPAY — 70: Standardized API Error Response Model Specification

## 1. Standard Error JSON Response Schema

```json
{
  "error": {
    "code": "PAYMENT_POLICY_VIOLATED",
    "message": "Payment amount (₹25,000) exceeds single transaction policy limit (₹10,000).",
    "details": {
      "limit": 1000000,
      "requested": 2500000
    },
    "request_id": "req_7f8a9b0c",
    "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
    "timestamp": "2026-08-24T23:13:00Z"
  }
}
```

Internal stack traces, SQL errors, and secret API keys are strictly excluded from API error payloads.
