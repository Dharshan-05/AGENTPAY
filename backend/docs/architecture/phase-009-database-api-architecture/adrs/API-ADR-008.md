# API-ADR-008: Mandatory Ingress `Idempotency-Key` Header Enforcement

## Context & Problem Statement
Preventing duplicate financial transaction clearing under client network retries.

## Decision
Mandate client UUID v4 `Idempotency-Key` headers on state-mutating payment and refund endpoints.

## Consequences & Trade-Offs
* **Benefits**: Replays identical responses safely for duplicate requests.
* **Trade-Offs**: Rejects requests lacking idempotency headers with HTTP 400.
