"""Pydantic Transport Schemas for Offer Optimization Subsystem (Phase 179)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OptimizedOfferItem(BaseModel):
    """Payload contract for optimal offer evaluation result (Phase 179)."""

    model_config = ConfigDict(extra="forbid")

    offer_id: uuid.UUID = Field(..., description="Optimal Offer UUID")
    name: str = Field(..., description="Offer title/name")
    slug: str = Field(..., description="Offer unique slug")
    unit_price: Decimal = Field(..., description="Original product unit price")
    discounted_unit_price: Decimal = Field(..., description="Discounted unit price")
    quantity: Decimal = Field(..., description="Evaluated purchase quantity")
    original_total: Decimal = Field(..., description="Gross total before offer discount")
    discount_amount: Decimal = Field(..., description="Total savings / discount amount")
    final_total: Decimal = Field(..., description="Net total payable after discount")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    effective_savings_pct: float = Field(
        ..., ge=0.0, le=100.0, description="Effective savings percentage"
    )  # noqa: E501


class OfferOptimizationResponse(BaseModel):
    """Response payload for offer optimization (Phase 179)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    quantity: Decimal = Field(..., description="Evaluated quantity")
    has_applicable_offer: bool = Field(
        ..., description="True if a valid applicable offer was selected"
    )  # noqa: E501
    optimized_offer: OptimizedOfferItem | None = Field(
        default=None, description="Optimal offer evaluation result, if any"
    )
