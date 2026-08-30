# DB-ADR-018: Immutable SHA-256 Block Chain Security Audit Table

## Context & Problem Statement
Security audit logs must be mathematically tamper-evident to prevent insider data manipulation.

## Decision
Maintain an append-only `audit_events` table where every row links the SHA-256 block hash of the previous row.

## Consequences & Trade-Offs
* **Benefits**: Mathematically proves audit log chain integrity.
* **Trade-Offs**: Requires calculating SHA-256 hashes during insert.
