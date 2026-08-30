"""Pydantic Transport Schemas for Merchant Domain Service (Phase 165)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class MerchantStatusEnum(StrEnum):
    """Controlled lifecycle status for Merchant entity (Phase 165)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class MerchantCreateRequest(StrictRequestModel):
    """Request contract to create a new Merchant (Phase 165)."""

    name: str = Field(..., min_length=1, max_length=255, description="Business name")
    slug: str | None = Field(
        default=None, max_length=100, description="Optional custom URL/identifier slug"
    )
    description: str | None = Field(
        default=None, max_length=500, description="Merchant description"
    )  # noqa: E501
    status: MerchantStatusEnum = Field(
        default=MerchantStatusEnum.ACTIVE, description="Initial merchant status"
    )


class MerchantUpdateRequest(StrictRequestModel):
    """Request contract to update an existing Merchant (Phase 165)."""

    name: str | None = Field(default=None, min_length=1, max_length=255, description="Updated name")
    description: str | None = Field(default=None, max_length=500, description="Updated description")
    status: MerchantStatusEnum | None = Field(default=None, description="Updated status")


class MerchantResponse(BaseModel):
    """Response contract returning Merchant details (Phase 165)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Merchant primary key UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    name: str = Field(..., description="Business name")
    slug: str = Field(..., description="Identifier slug")
    status: MerchantStatusEnum = Field(..., description="Lifecycle status")
    description: str | None = Field(default=None, description="Description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: datetime | None = Field(default=None, description="Archival/deletion timestamp")


class MerchantListResponse(BaseModel):
    """Paginated list response contract for Merchant entities (Phase 165)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_count: int = Field(..., description="Count of items in current page")
    has_more: bool = Field(..., description="True if next page exists")
    merchants: list[MerchantResponse] = Field(default_factory=list, description="Merchant items")
