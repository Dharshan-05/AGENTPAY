"""Pydantic Transport Schemas for Purchase Planning Subsystem (Phase 180)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchasePlanItemRequest(BaseModel):
    """Line item contract for purchase plan creation (Phase 180)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    quantity: Decimal = Field(..., gt=0.0, description="Desired purchase quantity (> 0)")


class PurchasePlanItemResponse(BaseModel):
    """Line item response snapshot in purchase plan (Phase 180)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    unit_price: Decimal = Field(..., description="Base product unit price")
    quantity: Decimal = Field(..., description="Purchased quantity")
    selected_offer_id: uuid.UUID | None = Field(
        default=None, description="Optimal commercial offer UUID applied"
    )
    discount_amount: Decimal = Field(..., description="Line discount savings")
    line_total: Decimal = Field(..., description="Net line total payable")
    currency_code: str = Field(..., description="ISO 4217 currency code")


class PurchasePlanCreateRequest(BaseModel):
    """Request contract for creating a structured purchase plan (Phase 180)."""

    model_config = ConfigDict(extra="forbid")

    items: list[PurchasePlanItemRequest] = Field(
        ..., min_length=1, max_length=50, description="List of 1 to 50 line items"
    )
    agent_id: uuid.UUID | None = Field(
        default=None, description="Optional Agent UUID creating plan"
    )
    idempotency_key: str | None = Field(
        default=None,
        max_length=100,
        description="Optional idempotency key for replay protection",  # noqa: E501
    )


class PurchasePlanResponse(BaseModel):
    """Response payload for purchase plan (Phase 180)."""

    model_config = ConfigDict(extra="forbid")

    plan_id: uuid.UUID = Field(..., description="Purchase Plan UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Agent UUID")
    plan_reference: str = Field(..., description="Unique plan reference identifier")
    status: str = Field(..., description="Plan status (draft, validated, ready)")
    items: list[PurchasePlanItemResponse] = Field(
        default_factory=list, description="Plan line items snapshot"
    )
    subtotal: Decimal = Field(..., description="Gross subtotal before discounts")
    discount_total: Decimal = Field(..., description="Total plan discount savings")
    total_amount: Decimal = Field(..., description="Net total payable amount")
    currency_code: str = Field(..., description="Unified plan ISO currency code")
    planned_at: datetime = Field(..., description="Planning creation timestamp")
