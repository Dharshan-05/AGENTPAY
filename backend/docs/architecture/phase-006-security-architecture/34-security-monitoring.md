# AGENTPAY — 34: Security Event Logging & Real-Time SIEM Monitoring

## 1. Security Event Schema

Every security event emits a structured JSON log record to the SIEM processing engine:

```json
{
  "event_id": "sec_8f7a6b5c",
  "event_type": "SECURITY_CRITICAL_RISK_DETECTED",
  "severity": "P0",
  "actor": { "user_id": "usr_91a0", "agent_id": "agt_8f9b" },
  "tenant_id": "tenant_7f8a",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "timestamp": "2026-08-24T21:40:00Z",
  "details": { "risk_score": 94, "category": "Gambling", "action": "AUTO_SUSPEND_AGENT" }
}
```
