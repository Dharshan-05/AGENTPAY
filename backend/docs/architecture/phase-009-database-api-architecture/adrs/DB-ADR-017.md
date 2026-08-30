# DB-ADR-017: Transactional Outbox Pattern for Atomic Event Delivery

## Context & Problem Statement
Updating the database and publishing events to a message bus in separate calls risks dual-write event loss.

## Decision
Write domain events into `outbox_events` inside the same database transaction, polled asynchronously by outbox worker processes.

## Consequences & Trade-Offs
* **Benefits**: 100% atomic state update and event creation.
* **Trade-Offs**: Requires background worker polling process.
