"""Pydantic Transport Schemas for Product Domain Service (Phase 164)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class ProductStatusEnum(StrEnum):
    """Controlled lifecycle status for Product entity (Phase 164)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DISCONTINUED = "discontinued"


class ProductCreateRequest(StrictRequestModel):
    """Request contract to create a new Product (Phase 164)."""

    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Product title/name")
    sku: str = Field(
        ..., min_length=1, max_length=100, description="Product Stock Keeping Unit (SKU)"
    )  # noqa: E501
    description: str | None = Field(
        default=None, max_length=1000, description="Product description"
    )  # noqa: E501
    price: Decimal = Field(..., gt=0.0, description="Financial price (greater than zero)")  # noqa: E501
    currency_code: str = Field(
        default="USD", min_length=3, max_length=3, description="ISO 4217 currency code"
    )
    status: ProductStatusEnum = Field(
        default=ProductStatusEnum.ACTIVE, description="Initial product status"
    )
    metadata_payload: dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata payload"
    )


class ProductUpdateRequest(StrictRequestModel):
    """Request contract to update an existing Product (Phase 164)."""

    name: str | None = Field(default=None, min_length=1, max_length=255, description="Updated name")
    description: str | None = Field(
        default=None, max_length=1000, description="Updated description"
    )  # noqa: E501
    price: Decimal | None = Field(default=None, gt=0.0, description="Updated price")
    currency_code: str | None = Field(
        default=None, min_length=3, max_length=3, description="Updated currency code"
    )
    status: ProductStatusEnum | None = Field(default=None, description="Updated product status")
    metadata_payload: dict[str, Any] | None = Field(
        default=None, description="Updated metadata payload"
    )


class ProductResponse(BaseModel):
    """Response contract returning Product details (Phase 164)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Product primary key UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Stock Keeping Unit (SKU)")
    description: str | None = Field(default=None, description="Product description")
    status: ProductStatusEnum = Field(..., description="Lifecycle status")
    price: Decimal = Field(..., description="Financial price decimal")
    currency_code: str = Field(..., description="ISO currency code")
    metadata_payload: dict[str, Any] = Field(default_factory=dict, description="Metadata payload")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: datetime | None = Field(default=None, description="Archival/deletion timestamp")


class ProductListResponse(BaseModel):
    """Paginated list response contract for Product entities (Phase 164)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_count: int = Field(..., description="Count of items in current page")
    has_more: bool = Field(..., description="True if next page exists")
    products: list[ProductResponse] = Field(default_factory=list, description="Product items")
