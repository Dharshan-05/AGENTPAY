"""Base Product & Seller Data Provider Abstraction."""

from __future__ import annotations

import abc
from decimal import Decimal
from typing import Any

from app.commerce.schemas import NormalizedProduct, SellerInfo


class BaseProductSearchProvider(abc.ABC):
    """Abstract provider interface for online product discovery and seller intelligence."""

    @abc.abstractmethod
    async def search_products(
        self,
        query: str,
        category: str | None = None,
        max_price: Decimal | None = None,
        min_rating: float | None = None,
        purpose: str | None = None,
        limit: int = 10,
    ) -> list[NormalizedProduct]:
        """Search and discover products matching query and constraints."""
        ...

    @abc.abstractmethod
    async def get_product_details(self, product_id: str) -> NormalizedProduct | None:
        """Fetch detailed normalized product metadata."""
        ...

    @abc.abstractmethod
    async def get_seller_info(self, seller_id: str) -> SellerInfo | None:
        """Fetch seller reputation, rating, return policy, and risk signals."""
        ...
