# AGENTPAY Architecture Specification: Phase 171 — Product Sorting

## Overview
Phase 171 establishes a safe, deterministic product sorting subsystem with SQL injection protection.

## Sort Whitelist & Injection Defense
Sort column names are mapped server-side via `SORT_COLUMN_MAP`:
```python
SORT_COLUMN_MAP = {
    "created_at": Product.created_at,
    "updated_at": Product.updated_at,
    "name": Product.name,
    "price": Product.price,
    "sku": Product.sku,
}
```
Client input outside this whitelist defaults safely to `created_at`.

## Deterministic Tie-Breaking & Directions
- Supported directions: `asc`, `desc`.
- Tie-breaker: Always appends `Product.id.asc()` or `Product.id.desc()` to guarantee deterministic keyset pagination ordering.
