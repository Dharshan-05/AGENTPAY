# DB-ADR-002: Cryptographic Prefixed Identifier Strategy

## Context & Problem Statement
Sequential integer primary keys risk enumeration attacks; raw UUIDs lack domain context readability.

## Decision
Adopt 128-bit UUID v4 identifiers with domain prefix strings (e.g. `pay_7f8a9b0c-1d2e`).

## Consequences & Trade-Offs
* **Benefits**: Enumeration resistant; instant domain object context identification.
* **Trade-Offs**: Slightly larger index storage footprint than 64-bit integers.
