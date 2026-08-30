"""Pydantic Transport Schemas for Product Ranking (Phase 173)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RankedProductItem(BaseModel):
    """Single ranked product item payload with explainable scoring (Phase 173)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., description="Financial price")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    status: str = Field(..., description="Product status")
    ranking_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall explainable ranking score"
    )  # noqa: E501
    semantic_score: float = Field(
        ..., ge=0.0, le=1.0, description="Vector similarity component score"
    )  # noqa: E501
    keyword_score: float = Field(
        ..., ge=0.0, le=1.0, description="Keyword text match component score"
    )  # noqa: E501
    business_score: float = Field(
        ..., ge=0.0, le=1.0, description="Business status component score"
    )  # noqa: E501
    freshness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Recency freshness component score"
    )  # noqa: E501
    ranking_reasons: list[str] = Field(
        default_factory=list, description="Human-readable ranking explanation signals"
    )


class ProductRankingResponse(BaseModel):
    """Product ranking response payload (Phase 173)."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., description="Executed search/ranking query")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_count: int = Field(..., description="Count of ranked product items")
    results: list[RankedProductItem] = Field(
        default_factory=list, description="Ranked product items"
    )  # noqa: E501
