# AGENTPAY Architecture Specification: Phase 179 — Offer Optimization

## Overview
Phase 179 establishes a deterministic offer optimization service (`OfferOptimizationService`) for selecting the single best commercial offer for a product/quantity context.

## Optimization Objective & Deterministic Tie-Breaking
- **Service Layer**: Reuses `OfferService.get_product_offers` to fetch valid, active offers in tenant scope.
- **Evaluation Criteria**: Calculates `original_total`, `discount_amount`, `final_total`, and `effective_savings_pct` using `Decimal(18, 4)` precision. Zero float usage.
- **Tie-Breaking Rule**:
  1. Highest `discount_amount`
  2. Highest `effective_savings_pct`
  3. Earliest `ends_at` expiration timestamp
  4. `offer_id` ASC (UUID string compare)
- **REST Endpoint**: `GET /api/v1/products/{product_id}/offers/optimize?quantity=1`.
