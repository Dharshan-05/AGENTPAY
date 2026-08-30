# PAY-ADR-008: 4-Layer Defense-in-Depth Duplicate Prevention

## 1. Context & Problem Statement
Relying on a single idempotency check is insufficient against distributed race conditions.

## 2. Decision
Implement 4 defense layers: 1) Redis lock, 2) DB unique constraints, 3) State machine preconditions, 4) Razorpay order idempotency.

## 3. Consequences & Trade-Offs
* **Benefits**: 100% protection against double-spend events.
* **Trade-Offs**: Requires multi-layer key handling logic.
