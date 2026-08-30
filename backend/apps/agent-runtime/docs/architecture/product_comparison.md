# AGENTPAY Architecture Specification: Phase 172 — Product Comparison

## Overview
Phase 172 introduces side-by-side product comparison (`ProductComparisonService`) for 2 to 5 products within tenant isolation boundary.

## Comparison Rules & Financial Metrics
- **Bounded Input**: Accepts 2 to 5 distinct product UUIDs. Rejects `< 2`, `> 5`, or duplicate IDs.
- **Tenant Security & Anti-Enumeration**: Validates all requested product IDs against `tenant_id` and active status. Missing or cross-tenant products return `404 Not Found`.
- **Financial Precision (`Decimal`)**: Computes `lowest_price_product_id`, `highest_price_product_id`, and `price_difference`.
- **Cross-Currency Protection**: If compared products span multiple different currencies (e.g. USD vs EUR), sets `common_currency = None` and `price_difference_available = False` without performing cross-currency arithmetic.
- **REST Endpoint**: `GET /api/v1/products/compare?product_ids=id1,id2,id3`.
