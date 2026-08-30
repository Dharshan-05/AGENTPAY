# DB-ADR-015: Zero-Downtime Expand/Contract Database Migration Strategy

## Context & Problem Statement
Modifying database schemas in production must not cause downtime or broken API queries.

## Decision
Mandate the Expand/Contract migration pattern (Phase 1: Expand column, Phase 2: Dual-write, Phase 3: Backfill, Phase 4: Contract).

## Consequences & Trade-Offs
* **Benefits**: 100% zero-downtime database deployment.
* **Trade-Offs**: Requires multi-step deployment pipelines for schema changes.
