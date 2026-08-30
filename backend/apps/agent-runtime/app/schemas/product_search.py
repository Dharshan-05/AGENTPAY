"""Pydantic Transport Schemas for Product Search & Semantic Search (Phase 168 & 169)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductSearchResult(BaseModel):
    """Single keyword search result contract (Phase 168)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., description="Financial price")
    currency_code: str = Field(..., description="ISO currency code")
    status: str = Field(..., description="Product status")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Keyword text relevance score")
    match_type: str = Field(
        ..., description="Match category (EXACT_SKU, EXACT_NAME, NAME_MATCH, DESCRIPTION_MATCH)"
    )  # noqa: E501


class ProductSearchResponse(BaseModel):
    """Keyword search response list contract (Phase 168)."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., description="Executed search query string")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    total_count: int = Field(..., description="Count of matched products")
    has_more: bool = Field(..., description="True if next page exists")
    results: list[ProductSearchResult] = Field(
        default_factory=list, description="Matched search items"
    )  # noqa: E501


class SemanticProductSearchResult(BaseModel):
    """Single semantic search result contract (Phase 169)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Product UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    merchant_id: uuid.UUID = Field(..., description="Parent Merchant UUID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: Decimal = Field(..., description="Financial price")
    currency_code: str = Field(..., description="ISO currency code")
    status: str = Field(..., description="Product status")
    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Vector cosine similarity score")
    keyword_score: float = Field(..., ge=0.0, le=1.0, description="Keyword text relevance score")
    hybrid_score: float = Field(
        ..., ge=0.0, le=1.0, description="Combined deterministic hybrid relevance score"
    )  # noqa: E501


class SemanticProductSearchResponse(BaseModel):
    """Semantic search response list contract (Phase 169)."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., description="Executed search query string")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    hybrid_enabled: bool = Field(..., description="True if hybrid scoring was applied")
    total_count: int = Field(..., description="Count of semantic search results")
    results: list[SemanticProductSearchResult] = Field(
        default_factory=list, description="Matched items"
    )  # noqa: E501
