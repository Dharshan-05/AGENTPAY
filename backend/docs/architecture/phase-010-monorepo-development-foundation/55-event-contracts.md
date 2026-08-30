# AGENTPAY — 55: Domain Event Payload Schemas & Outbox Serialization

## 1. Outbox Event Contract

```typescript
export interface DomainEvent<T = Record<string, unknown>> {
  event_id: string;
  event_type: string;
  event_version: string;
  tenant_id: string;
  aggregate_id: string;
  timestamp: string;
  trace_id: string;
  payload: T;
}
```
