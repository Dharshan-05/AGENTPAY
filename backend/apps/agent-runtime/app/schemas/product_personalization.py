"""Pydantic Transport Schemas for Product Personalization (Phase 175)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PersonalizedProductItem(BaseModel):
    """Single personalized product item payload (Phase 175)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., description="Financial price")
    currency_code: str = Field(..., description="ISO 4217 currency code")
    status: str = Field(..., description="Product status")
    base_rank_score: float = Field(..., ge=0.0, le=1.0, description="Base product ranking score")
    personalization_boost: float = Field(
        ..., ge=0.0, le=0.2, description="Bounded personalization boost score"
    )  # noqa: E501
    final_score: float = Field(..., ge=0.0, le=1.0, description="Final combined personalized score")
    personalization_signals: list[str] = Field(
        default_factory=list, description="Extracted memory preference signals applied"
    )


class PersonalizedRecommendationResponse(BaseModel):
    """Personalized recommendation response payload (Phase 175)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    user_id: uuid.UUID | None = Field(default=None, description="Authenticated user UUID")
    agent_id: uuid.UUID | None = Field(default=None, description="Authenticated agent UUID")
    personalization_applied: bool = Field(
        ..., description="True if memory-based preferences were matched"
    )  # noqa: E501
    total_count: int = Field(..., description="Count of personalized product items")
    results: list[PersonalizedProductItem] = Field(
        default_factory=list, description="Personalized items"
    )  # noqa: E501
