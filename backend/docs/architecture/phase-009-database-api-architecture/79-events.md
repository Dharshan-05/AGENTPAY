# AGENTPAY — 79: Standardized Domain Event Schema Architecture

## 1. Event Payload JSON Schema

```json
{
  "event_id": "evt_7f8a9b0c-1d2e",
  "event_type": "PaymentAuthorized",
  "event_version": "1.0",
  "tenant_id": "tenant_7f8a9b0c",
  "aggregate_id": "intent_7f8a9b0c",
  "timestamp": "2026-08-24T23:14:00Z",
  "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736",
  "payload": {
    "payment_intent_id": "intent_7f8a9b0c",
    "agent_id": "agt_8f9b2c3a",
    "amount": 250000,
    "currency": "INR"
  }
}
```
