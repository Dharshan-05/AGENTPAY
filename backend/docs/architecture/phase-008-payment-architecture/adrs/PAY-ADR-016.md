# PAY-ADR-016: Transactional Outbox Pattern for Atomic Event Dispatch

## 1. Context & Problem Statement
Updating the payment database and publishing events to a message queue in separate calls risks dual-write event loss.

## 2. Decision
Use the Transactional Outbox Pattern, writing events to an `outbox_events` table within the same DB transaction, polled asynchronously by workers.

## 3. Consequences & Trade-Offs
* **Benefits**: Guarantees atomic event persistence and delivery.
* **Trade-Offs**: Requires background worker process polling the outbox table.
