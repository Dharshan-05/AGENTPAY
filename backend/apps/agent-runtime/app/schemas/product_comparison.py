"""Pydantic Transport Schemas for Product Comparison (Phase 172)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductComparisonItem(BaseModel):
    """Single compared product item payload (Phase 172)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., description="Financial price")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    status: str = Field(..., description="Product status")


class ProductComparisonMetrics(BaseModel):
    """Calculated comparison metrics across products (Phase 172)."""

    model_config = ConfigDict(extra="forbid")

    product_count: int = Field(..., description="Number of products compared")
    common_currency: str | None = Field(
        default=None,
        description="ISO currency code if all items share the same currency, else None",  # noqa: E501
    )
    lowest_price_product_id: uuid.UUID | None = Field(
        default=None, description="Product UUID with the lowest price"
    )
    highest_price_product_id: uuid.UUID | None = Field(
        default=None, description="Product UUID with the highest price"
    )
    lowest_price: Decimal | None = Field(default=None, description="Lowest price value")
    highest_price: Decimal | None = Field(default=None, description="Highest price value")
    price_difference: Decimal | None = Field(
        default=None, description="Decimal price difference if common currency exists, else None"
    )
    price_difference_available: bool = Field(
        ..., description="True if price comparison is valid and common currency exists"
    )


class ProductComparisonResponse(BaseModel):
    """Product comparison response payload (Phase 172)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    products: list[ProductComparisonItem] = Field(
        default_factory=list, description="List of compared product details"
    )
    metrics: ProductComparisonMetrics = Field(..., description="Calculated comparison metrics")
