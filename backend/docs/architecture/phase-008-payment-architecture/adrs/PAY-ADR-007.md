# PAY-ADR-007: Multi-Tier Redis 24-Hour Idempotency Locking

## Context & Problem Statement
Network retries or client double-clicks can cause duplicate payment settlements.

## Decision
Mandate client-provided `idempotency_key` headers locked in Redis for 24 hours via `SETNX`.

## Consequences & Trade-Offs
* **Benefits**: Replays identical responses safely for duplicate requests.
* **Trade-Offs**: Requires client applications to send UUID v4 idempotency keys.
