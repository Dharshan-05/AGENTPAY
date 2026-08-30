# API-ADR-009: Opaque Cursor-Based Pagination Architecture

## Context & Problem Statement
Deep SQL offset pagination (`OFFSET 10000`) causes severe performance degradation on large tables.

## Decision
Ban offset pagination; mandate opaque base64 cursor pagination (`cursor`, `limit`, `next_cursor`, `has_more`).

## Consequences & Trade-Offs
* **Benefits**: Constant-time $O(1)$ query performance across millions of rows.
* **Trade-Offs**: Clients cannot jump directly to arbitrary page numbers.
