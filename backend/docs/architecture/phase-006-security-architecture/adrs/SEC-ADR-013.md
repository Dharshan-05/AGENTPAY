# SEC-ADR-013: Append-Only Cryptographic SHA-256 Audit Chain

## Context & Problem Statement
Financial security requires non-repudiable, tamper-evident audit trails for regulatory compliance and dispute resolution.

## Threat Analysis
An insider or compromised service could modify or delete past transaction audit logs to conceal fraudulent activity.

## Decision
Construct an append-only cryptographic block hash chain ($H_n = \text{SHA256}(H_{n-1} \parallel \dots)$). Deny `UPDATE` and `DELETE` database privileges on `audit_logs`.

## Consequences & Trade-Offs
* **Benefits**: Guarantees mathematical tamper-evidence for all historical audit logs.
* **Trade-Offs**: Requires appending block hashes sequentially in background worker queues.
