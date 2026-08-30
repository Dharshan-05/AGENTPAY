# AGENTPAY Architecture Specification: Phase 174 — Recommendation Engine

## Overview
Phase 174 implements the recommendation engine (`RecommendationService`) producing bounded, deduplicated product recommendations.

## Recommendation Rules & Invariants
- **Supported Types**: `similar_products`, `related_products`.
- **Target Product Self-Exclusion**: Target product is automatically excluded (`p.id != target_product_id`).
- **Deduplication**: Candidates are deduplicated by `product_id`.
- **Tenant Isolation**: Strictly tenant-scoped (`tenant_id`). Excludes inactive and soft-deleted items.
- **REST Endpoint**: `GET /api/v1/products/recommendations?recommendation_type=similar_products&target_product_id={id}&limit=10`.
