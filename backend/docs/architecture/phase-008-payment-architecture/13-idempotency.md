# AGENTPAY — 13: Multi-Tier Redis 24-Hour Idempotency Locking

## 1. Idempotency Lock Protocol

All payment creation, authorization, execution, and refund endpoints mandate client-provided `idempotency_key` headers (UUID v4).

$$\text{Redis Key} = \text{idempotency:tenant:}\langle \text{tenant\_id} \rangle \text{:key:}\langle \text{idempotency\_key} \rangle$$

---

## 2. Collision & Replay Resolution

1. **First Request**: Acquires Redis 24-hour lock via `SETNX`; processes transaction; caches response payload in Redis.
2. **Identical Replay (Same Payload)**: Returns cached HTTP response payload immediately without re-executing settlement.
3. **Mismatched Replay (Different Payload)**: Rejects request with HTTP 409 Conflict (`ERR_IDEMPOTENCY_KEY_REUSE`).
