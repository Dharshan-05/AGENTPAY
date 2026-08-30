# AGENTPAY — 51: Standardized JSON Logging Format & Redaction Rules

## 1. JSON Log Format

```json
{
  "timestamp": "2026-08-25T07:50:00.000Z",
  "level": "info",
  "message": "Payment intent authorized successfully",
  "tenant_id": "tenant_demo_acme",
  "agent_id": "agt_shopping_01",
  "payment_intent_id": "intent_7f8a9b0c",
  "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}
```

Sensitve fields (`password`, `jwt`, `razorpay_secret`) are automatically redacted by logger formatters.
