# AGENTPAY — 24: Webhook Event Deduplication & Replay Prevention

## 1. Deduplication Rules

* **Event ID Lock**: Redis 7-day key check on `webhook:event:<provider_event_id>`.
* **Duplicate Event**: HTTP 200 OK returned immediately; background processing skipped.
* **Payload Hash Mutation Alert**: If duplicate `event_id` arrives with a altered payload hash, system logs `CRITICAL_WEBHOOK_PAYLOAD_MUTATION` security alert.
