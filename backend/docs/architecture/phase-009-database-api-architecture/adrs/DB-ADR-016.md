# DB-ADR-016: Continuous Write-Ahead Log (WAL) Archiving & PITR

## Context & Problem Statement
Protecting financial database records against data loss or corruption.

## Decision
Stream PostgreSQL Write-Ahead Logs (WAL) continuously to encrypted S3/GCS buckets, enabling microsecond Point-In-Time Recovery (PITR).

## Consequences & Trade-Offs
* **Benefits**: RPO $< 1\text{ second}$ financial recovery capability.
* **Trade-Offs**: Requires storage budget for continuous WAL log retention.
