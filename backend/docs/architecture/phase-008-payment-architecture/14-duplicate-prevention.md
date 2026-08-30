# AGENTPAY — 14: Multi-Level Double-Spend & Duplicate Execution Defenses

## 1. Multi-Level Defense Layers

```
[ Ingress API Gateway ] ──> Layer 1: Redis 24h Idempotency Lock
                                │
[ Relational Datastore ] ──> Layer 2: PostgreSQL Unique Key Constraint (tenant_id, idempotency_key)
                                │
[ Payment Orchestrator ] ──> Layer 3: State Machine Precondition (State == AUTHORIZED)
                                │
[ Razorpay API Gateway ] ──> Layer 4: Razorpay Provider Order Idempotency Key
```

This 4-layer defense-in-depth architecture renders duplicate payment clearing mathematically impossible under client retries, network glitches, or parallel worker execution.
