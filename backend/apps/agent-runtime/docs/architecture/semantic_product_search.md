# AGENTPAY Architecture Specification: Phase 169 — Semantic Product Search

## Overview
Phase 169 introduces natural language semantic product search using vector embeddings and hybrid relevance scoring.

## Embedding Architecture
`EmbeddingService` computes normalized 128-dimensional vector embeddings for query text and product metadata (`name + sku + description`).

## Similarity Metric & Hybrid Scoring
- Vector Cosine Similarity: `dot_product(query_vec, product_vec)` of normalized 128-d vectors (returns `0.0` to `1.0`).
- Hybrid Relevance Scoring: `hybrid_score = (keyword_weight * keyword_score) + (semantic_weight * semantic_score)` (default weights: `0.5 / 0.5`).

## Invariants & Security
- **Tenant Isolation**: Vector search is strictly tenant-scoped (`tenant_id`).
- **Zero Raw Vectors**: Raw vector embeddings are never exposed in API responses.
- **REST Endpoint**: `GET /api/v1/products/semantic-search?q={query}&limit=20&hybrid=true`.
