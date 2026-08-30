# MONO-ADR-018: Background Worker Execution Architecture (`apps/worker`)

## Context & Problem Statement
Preventing long-running asynchronous tasks (outbox event publishing, webhook callbacks, reconciliation) from blocking HTTP API response loops.

## Decision
Decouple background execution into `apps/worker`, polling PostgreSQL outbox events and consuming Redis task queues asynchronously.

## Consequences & Trade-Offs
* **Benefits**: Keeps API latency under 100ms by offloading background processing.
* **Trade-Offs**: Requires deploying and monitoring worker processes alongside API servers.
