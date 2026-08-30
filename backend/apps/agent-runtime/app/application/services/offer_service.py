"""Commercial Offer Application Service for AGENTPAY (Phase 178)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.domain.exceptions.agent_exceptions import ProductNotFoundError
from app.infrastructure.database.models.offer import Offer
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.offers import OfferItem, OfferListResponse

logger = logging.getLogger("agentpay.offer.service")


class OfferService:
    """Production service orchestrating commercial offer retrieval and evaluation (Phase 178)."""

    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    async def get_product_offers(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
        requested_quantity: Decimal = Decimal("1.000"),
    ) -> OfferListResponse:
        """Retrieve applicable commercial offers for a product (Phase 178)."""
        # 1. Verify Product exists fail-closed in tenant boundary
        product = await self.repository.get_by_id(db, tenant_id, product_id, include_deleted=False)
        if not product or product.status != "active":
            raise ProductNotFoundError(f"Product '{product_id}' not found or inactive.")

        # 2. Query Offer ORM entities for product
        stmt = select(Offer).where(
            Offer.tenant_id == tenant_id,
            Offer.product_id == product_id,
            Offer.status == "active",
            Offer.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        raw_offers = list(res.scalars().all())

        now = datetime.now(UTC)
        applicable_items: list[OfferItem] = []

        prod_currency = getattr(product, "currency_code", None) or "USD"

        for off in raw_offers:
            # Check date bounds
            if off.starts_at and off.starts_at.replace(tzinfo=UTC) > now:
                continue
            if off.ends_at and off.ends_at.replace(tzinfo=UTC) <= now:
                continue

            # Check quantity bounds
            if off.min_quantity and requested_quantity < off.min_quantity:
                continue
            if off.max_quantity and requested_quantity > off.max_quantity:
                continue

            # Currency safety check
            off_currency = off.currency_code or "USD"
            if off_currency != prod_currency:
                logger.warning(
                    "Offer %s currency (%s) does not match product currency (%s)",
                    off.id,
                    off_currency,
                    prod_currency,
                )
                continue

            orig_price = product.price
            disc_price = off.price
            disc_amount = max(Decimal("0.00"), orig_price - disc_price)

            applicable_items.append(
                OfferItem(
                    offer_id=off.id,
                    tenant_id=off.tenant_id,
                    merchant_id=off.merchant_id,
                    product_id=off.product_id,
                    name=off.name,
                    slug=off.slug,
                    status=off.status,
                    original_price=orig_price,
                    discounted_price=disc_price,
                    discount_amount=disc_amount,
                    currency_code=prod_currency,
                    starts_at=off.starts_at,
                    ends_at=off.ends_at,
                )
            )

        return OfferListResponse(
            tenant_id=tenant_id,
            product_id=product_id,
            total_count=len(applicable_items),
            offers=applicable_items,
        )
