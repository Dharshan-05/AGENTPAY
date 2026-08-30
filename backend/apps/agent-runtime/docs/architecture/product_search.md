# AGENTPAY Architecture Specification: Phase 168 — Product Search

## Overview
Phase 168 introduces the keyword product search subsystem (`ProductSearchService`) in AGENTPAY's Commerce Engine.

## Search Architecture & Relevance Ranking
Keyword search operates over product `name`, `description`, and `sku` with deterministic relevance ordering:
1. Exact SKU match (`1.0`, `EXACT_SKU`)
2. Exact product name match (`0.9`, `EXACT_NAME`)
3. Name match / substring (`0.75` / `0.6`, `NAME_MATCH`)
4. Description match (`0.4`, `DESCRIPTION_MATCH`)

## Invariants & Security
- **Tenant Isolation**: Queries strictly filter `tenant_id = :authenticated_tenant`.
- **Status & Lifecycle Filter**: Excludes soft-deleted (`deleted_at IS NOT NULL`) and inactive/archived products.
- **REST Endpoint**: `GET /api/v1/products/search?q={query}&limit=20`.
