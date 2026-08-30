"""Offer Optimization Application Service for AGENTPAY (Phase 179)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC
from decimal import Decimal
from typing import Any

from app.application.services.offer_service import OfferService
from app.domain.exceptions.agent_exceptions import ProductValidationError
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.offer_optimization import OfferOptimizationResponse, OptimizedOfferItem

logger = logging.getLogger("agentpay.offer.optimization.service")


class OfferOptimizationService:
    """Production service for deterministic commercial offer optimization (Phase 179)."""

    def __init__(
        self,
        repository: ProductRepository | None = None,
        offer_service: OfferService | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.offer_service = offer_service or OfferService(self.repository)

    async def optimize_offer(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: Decimal = Decimal("1.000"),
    ) -> OfferOptimizationResponse:
        """Find optimal offer producing greatest valid customer savings (Phase 179)."""
        if quantity <= Decimal("0.000"):
            raise ProductValidationError("quantity must be greater than zero.")

        # 1. Fetch applicable active offers via OfferService
        offers_resp = await self.offer_service.get_product_offers(
            db, tenant_id, product_id, requested_quantity=quantity
        )

        if not offers_resp.offers:
            return OfferOptimizationResponse(
                tenant_id=tenant_id,
                product_id=product_id,
                quantity=quantity,
                has_applicable_offer=False,
                optimized_offer=None,
            )

        # 2. Compute financial metrics for each candidate offer
        candidates: list[tuple[OptimizedOfferItem, tuple[Decimal, float, float, str]]] = []

        for off in offers_resp.offers:
            orig_total = off.original_price * quantity
            discount_tot = off.discount_amount * quantity
            final_tot = max(Decimal("0.0000"), orig_total - discount_tot)

            sav_pct = (
                round(float(discount_tot / orig_total) * 100.0, 2)
                if orig_total > Decimal("0.0000")
                else 0.0
            )

            exp_timestamp = (
                off.ends_at.replace(tzinfo=UTC).timestamp() if off.ends_at else float("inf")
            )

            item = OptimizedOfferItem(
                offer_id=off.offer_id,
                name=off.name,
                slug=off.slug,
                unit_price=off.original_price,
                discounted_unit_price=off.discounted_price,
                quantity=quantity,
                original_total=orig_total,
                discount_amount=discount_tot,
                final_total=final_tot,
                currency_code=off.currency_code,
                effective_savings_pct=sav_pct,
            )

            # Tie-breaking key: (-discount_amount, -effective_savings_pct, exp_timestamp, str(offer_id))  # noqa: E501
            sort_key = (-discount_tot, -sav_pct, exp_timestamp, str(off.offer_id))
            candidates.append((item, sort_key))

        # 3. Sort deterministically to select best offer
        candidates.sort(key=lambda x: x[1])
        best_item = candidates[0][0]

        return OfferOptimizationResponse(
            tenant_id=tenant_id,
            product_id=product_id,
            quantity=quantity,
            has_applicable_offer=True,
            optimized_offer=best_item,
        )
