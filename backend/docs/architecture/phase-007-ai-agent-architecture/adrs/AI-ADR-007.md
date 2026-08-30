# AI-ADR-007: Segregated Multi-Tier Memory Subsystems

## Context & Problem Statement
Mixing conversational chat memory with long-term user preferences or transaction receipts leads to data pollution and security leaks.

## Decision
Segregate memory into distinct subsystems: Redis short-term session cache, PostgreSQL long-term preference store, PostgreSQL RLS semantic vector embeddings, and append-only transaction history.

## Consequences & Trade-Offs
* **Benefits**: Clean state separation and precise memory access control.
* **Trade-Offs**: Requires managing separate memory storage engines.
