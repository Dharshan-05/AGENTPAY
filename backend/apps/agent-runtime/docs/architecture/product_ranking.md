# AGENTPAY Architecture Specification: Phase 173 — Product Ranking

## Overview
Phase 173 establishes a transparent, multi-signal explainable product ranking subsystem (`ProductRankingService`) in AGENTPAY's Commerce Engine.

## Ranking Signals & Formula
Combines 4 normalized signals `[0.0, 1.0]`:
- **Semantic Vector Similarity** (`SEMANTIC_WEIGHT = 0.40`)
- **Keyword Match Relevance** (`KEYWORD_WEIGHT = 0.35`)
- **Business Status Quality** (`BUSINESS_WEIGHT = 0.15`)
- **Recency Freshness Decay** (`FRESHNESS_WEIGHT = 0.10`)

`ranking_score = 0.40 * sem_score + 0.35 * kw_score + 0.15 * biz_score + 0.10 * freshness_score`

## Explainability & Tie-Breaking
- Outputs `ranking_reasons: list[str]` explaining score composition.
- Deterministic tie-breaker: `ranking_score DESC, product_id ASC`.
- Bounded top-K candidates (`limit: int = 20`, max 100).
