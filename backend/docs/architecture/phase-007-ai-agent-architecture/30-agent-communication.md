# AGENTPAY — 30: Inter-Agent Message Authorization Protocol

## 1. Inter-Agent Payload Schema

All messages passed between agents enforce strict authorization headers:

```json
{
  "message_id": "msg_9f8a7b6c",
  "sender_agent_id": "agt_commerce_01",
  "receiver_agent_id": "agt_payment_02",
  "tenant_id": "tenant_7f8a",
  "task_id": "task_12345",
  "timestamp": "2026-08-24T22:00:00Z",
  "message_type": "PROPOSE_INTENT",
  "payload": { "amount": 250000, "merchant": "AirIndia" },
  "authorization_context_sig": "hmac_signature"
}
```
