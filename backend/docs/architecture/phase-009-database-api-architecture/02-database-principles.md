# AGENTPAY — 02: 20 Non-Negotiable Database Architectural Design Principles

## 1. Architectural Principles Overview

```
+-----------------------------------------------------------------------+
|              20 NON-NEGOTIABLE DATABASE ARCHITECTURAL PRINCIPLES       |
+-----------------------------------------------------------------------+
|  1. Relational Integrity First (PostgreSQL Foreign Keys & Constraints)|
|  2. Absolute Financial Correctness (Zero Floating Point Money)        |
|  3. Hardware-Enforced Multi-Tenant Isolation (PostgreSQL RLS Policies)|
|  4. Strict ACID Transaction Boundaries for Financial Mutations        |
|  5. Append-Only Immutable History for Ledger & Security Audit Logs     |
|  6. Multi-Tier Unique Constraints for Double-Spend & Duplicate Defenses|
|  7. Deterministic State Machine Transition Constraints in SQL          |
|  8. Transactional Outbox Pattern for Atomic Domain Event Publishing   |
|  9. Explicit ID Strategy (Decoupled GUIDs vs External Provider IDs)   |
| 10. Explicit Database Schema Versioning & Backward Compatible Migrations|
| 11. Zero Plaintext Secret Storage in Database Columns                 |
| 12. Pessimistic Row Locking (SELECT FOR UPDATE) for Concurrency Control|
| 13. Time-Based Table Partitioning for High-Volume Audit Log Scaling   |
| 14. Standardized UTC Distributed Timestamping (TIMESTAMPTZ)            |
| 15. Indexed Query Optimization (Composite & Partial Indexing)         |
| 16. Authoritative Database State Supremacy Over LLM Reasoning Claims  |
| 17. Multi-User Database Role Isolation (App, Migration, Read-Only)     |
| 18. Fail-Closed Default Exception Handling on Constraint Failures     |
| 19. Continuous WAL Archival & Point-In-Time Disaster Recovery (PITR)  |
| 20. Zero Direct API Table Access (Repository Layer Abstraction Only)  |
+-----------------------------------------------------------------------+
```
