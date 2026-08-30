# DB-ADR-001: PostgreSQL Primary Relational Persistence Engine

## Context & Problem Statement
Autonomous financial transactions require strict ACID transactional guarantees, relational integrity, row-level locking, and hardware-enforced tenant isolation.

## Decision
Select PostgreSQL 14+ as the primary authoritative database engine for AGENTPAY.

## Consequences & Trade-Offs
* **Benefits**: 100% ACID compliance, Row-Level Security (RLS) support, partial/composite indexing, JSONB support.
* **Trade-Offs**: Requires connection pooling (PgBouncer) for high concurrency.
