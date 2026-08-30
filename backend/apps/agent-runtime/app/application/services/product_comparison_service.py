"""Product Comparison Domain Application Service for AGENTPAY (Phase 172)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.domain.exceptions.agent_exceptions import (
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.product_comparison import (
    ProductComparisonItem,
    ProductComparisonMetrics,
    ProductComparisonResponse,
)

logger = logging.getLogger("agentpay.product.comparison.service")

_MIN_COMPARE_PRODUCTS = 2
_MAX_COMPARE_PRODUCTS = 5


class ProductComparisonService:
    """Production service for side-by-side product comparison and metrics calculation (Phase 172)."""  # noqa: E501

    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    async def compare_products(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_ids: list[uuid.UUID],
    ) -> ProductComparisonResponse:
        """Compare 2 to 5 products within tenant isolation boundary (Phase 172)."""
        if not product_ids:
            raise ProductValidationError("product_ids list cannot be empty.")

        if len(product_ids) < _MIN_COMPARE_PRODUCTS or len(product_ids) > _MAX_COMPARE_PRODUCTS:
            raise ProductValidationError(
                f"Product comparison requires between {_MIN_COMPARE_PRODUCTS} and {_MAX_COMPARE_PRODUCTS} product IDs."  # noqa: E501
            )

        # Check for duplicate product IDs
        if len(set(product_ids)) != len(product_ids):
            raise ProductValidationError("Duplicate product_ids provided for comparison.")

        compared_products: list[Product] = []

        # Fetch each product from repository fail-closed (tenant-isolated)
        for pid in product_ids:
            prod = await self.repository.get_by_id(db, tenant_id, pid, include_deleted=False)
            if not prod or prod.status != "active":
                raise ProductNotFoundError(f"Product '{pid}' not found or unavailable.")
            compared_products.append(prod)

        # Build comparison items
        items = [
            ProductComparisonItem(
                product_id=p.id,
                merchant_id=p.merchant_id,
                sku=p.sku,
                name=p.name,
                description=p.description,
                price=p.price,
                currency_code=getattr(p, "currency_code", None) or "USD",
                status=p.status,
            )
            for p in compared_products
        ]

        # Calculate metrics
        currencies = {item.currency_code for item in items}
        same_currency = len(currencies) == 1

        if same_currency:
            common_currency = list(currencies)[0]
            # Find lowest and highest price products
            sorted_by_price = sorted(items, key=lambda x: x.price)
            lowest = sorted_by_price[0]
            highest = sorted_by_price[-1]

            diff = highest.price - lowest.price
            metrics = ProductComparisonMetrics(
                product_count=len(items),
                common_currency=common_currency,
                lowest_price_product_id=lowest.product_id,
                highest_price_product_id=highest.product_id,
                lowest_price=lowest.price,
                highest_price=highest.price,
                price_difference=diff,
                price_difference_available=True,
            )
        else:
            metrics = ProductComparisonMetrics(
                product_count=len(items),
                common_currency=None,
                lowest_price_product_id=None,
                highest_price_product_id=None,
                lowest_price=None,
                highest_price=None,
                price_difference=None,
                price_difference_available=False,
            )

        return ProductComparisonResponse(
            tenant_id=tenant_id,
            products=items,
            metrics=metrics,
        )
