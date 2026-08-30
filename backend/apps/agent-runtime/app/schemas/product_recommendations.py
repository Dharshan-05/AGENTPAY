"""Pydantic Transport Schemas for Recommendation Engine (Phase 174)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RecommendationItem(BaseModel):
    """Single recommended product item payload (Phase 174)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., description="Financial price")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    status: str = Field(..., description="Product status")
    recommendation_score: float = Field(
        ..., ge=0.0, le=1.0, description="Recommendation relevance score"
    )  # noqa: E501
    recommendation_type: str = Field(
        ..., description="Recommendation category (similar_products, related_products)"
    )  # noqa: E501
    recommendation_reason: str = Field(..., description="Human-readable recommendation rationale")


class RecommendationResponse(BaseModel):
    """Recommendation engine response payload (Phase 174)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    recommendation_type: str = Field(..., description="Executed recommendation type")
    target_product_id: uuid.UUID | None = Field(
        default=None, description="Target product UUID for similarity context"
    )
    total_count: int = Field(..., description="Count of recommended products")
    results: list[RecommendationItem] = Field(default_factory=list, description="Recommended items")
