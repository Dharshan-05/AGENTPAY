# API-ADR-017: Prohibition of Generic Financial `PATCH` Endpoints

## 1. Context & Problem Statement
Generic `PATCH` updates allow clients to tamper with protected financial fields (e.g. updating `status` to `SUCCESS`).

## 2. Decision
Ban generic `PATCH /payments/{id}` endpoints. Financial state transitions occur strictly through explicit command endpoints (`/authorize`, `/execute`, `/cancel`, `/refund`).

## Consequences & Trade-Offs
* **Benefits**: Guarantees server-authoritative control over state machine transitions.
* **Trade-Offs**: Requires defining dedicated command controllers for each financial state transition.
