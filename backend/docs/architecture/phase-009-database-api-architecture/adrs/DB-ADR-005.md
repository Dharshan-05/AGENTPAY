# DB-ADR-005: Fixed-Point Financial Precision (`NUMERIC(18,4)`)

## Context & Problem Statement
Floating-point storage (`FLOAT`, `DOUBLE PRECISION`) introduces rounding errors in financial transactions.

## Decision
Store all financial amounts using PostgreSQL `NUMERIC(18,4)` and represent minor units as 64-bit integers in memory.

## Consequences & Trade-Offs
* **Benefits**: 100% mathematical precision with zero rounding drift.
* **Trade-Offs**: Requires explicit minor unit conversion logic.
