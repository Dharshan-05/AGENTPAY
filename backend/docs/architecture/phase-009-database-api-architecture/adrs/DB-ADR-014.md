# DB-ADR-014: Time-Based Table Partitioning for Audit & Outbox Tables

## Context & Problem Statement
High-volume logging tables (`audit_events`, `outbox_events`) grow rapidly, degrading index maintenance performance.

## Decision
Use PostgreSQL 14+ Range Partitioning by month on `created_at` for high-volume event tables.

## Consequences & Trade-Offs
* **Benefits**: Enables instant dropping of old partitions (`DROP TABLE`); maintains fast index execution.
* **Trade-Offs**: Requires automated creation of future monthly partition tables.
