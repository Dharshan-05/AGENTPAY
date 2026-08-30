# DB-ADR-019: Automated 7-Year Financial Data Retention & Archival Rule

## Context & Problem Statement
Regulatory compliance (RBI, GST India) mandates retaining financial records for 7 years minimum.

## Decision
Retain financial tables (`payments`, `refunds`, `ledger_entries`) in active storage for 7 years; move cold partitions to S3 Glacier after 12 months.

## Consequences & Trade-Offs
* **Benefits**: Guarantees legal compliance while controlling database disk usage.
* **Trade-Offs**: Requires managing archival partition storage.
