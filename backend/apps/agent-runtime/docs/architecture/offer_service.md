# AGENTPAY Architecture Specification: Phase 178 — Offer Service

## Overview
Phase 178 implements the commercial offer retrieval and evaluation service (`OfferService`) in AGENTPAY's Commerce Engine.

## Offer Evaluation & Financial Precision
- **ORM Reuse**: Reuses pre-existing `Offer` ORM entity in [`app/infrastructure/database/models/offer.py`](file:///d:/PROJECT/ANGENT-PAY/apps/agent-runtime/app/infrastructure/database/models/offer.py) mapped to `offers` table. Zero duplicate ORM entities created.
- **Validity Bounds**: Checks `status == "active"`, validity date bounds (`starts_at <= now < ends_at`), and requested quantity boundaries (`min_quantity <= requested_quantity <= max_quantity`).
- **Currency Safety**: Enforces `offer.currency_code == product.currency_code`. Offers with currency mismatch are safely excluded.
- **Financial Precision**: All calculations (`original_price`, `discounted_price`, `discount_amount`) use `Decimal(18, 4)` precision. Zero float usage.
- **REST Endpoint**: `GET /api/v1/products/{product_id}/offers?quantity=1`.
