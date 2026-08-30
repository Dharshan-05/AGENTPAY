"""Pydantic Transport Schemas for Commercial Offer Service (Phase 178)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OfferItem(BaseModel):
    """Single commercial offer evaluation payload (Phase 178)."""

    model_config = ConfigDict(extra="forbid")

    offer_id: uuid.UUID = Field(..., description="Offer UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    name: str = Field(..., description="Offer title/name")
    slug: str = Field(..., description="Offer unique slug")
    status: str = Field(..., description="Offer status (active)")
    original_price: Decimal = Field(..., description="Original product list price")
    discounted_price: Decimal = Field(..., description="Effective discounted offer price")
    discount_amount: Decimal = Field(..., description="Savings / discount value")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    starts_at: datetime | None = Field(default=None, description="Offer start validity timestamp")
    ends_at: datetime | None = Field(default=None, description="Offer expiration timestamp")


class OfferListResponse(BaseModel):
    """Commercial offer list response payload (Phase 178)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    total_count: int = Field(..., description="Count of applicable offers")
    offers: list[OfferItem] = Field(
        default_factory=list, description="Applicable commercial offers"
    )  # noqa: E501
