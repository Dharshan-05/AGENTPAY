"""Pydantic Transport Schemas for Inventory Check & Validation (Phase 176 & 177)."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InventoryCheckResult(BaseModel):
    """Result payload for single product inventory availability check (Phase 176)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    requested_quantity: Decimal = Field(..., description="Requested quantity check")
    available_quantity: Decimal = Field(..., description="Currently available quantity in stock")
    is_available: bool = Field(..., description="True if available_quantity >= requested_quantity")
    inventory_status: str = Field(
        ...,
        description="Stock availability status (AVAILABLE, PARTIALLY_AVAILABLE, UNAVAILABLE, UNKNOWN)",  # noqa: E501
    )


class InventoryValidationItem(BaseModel):
    """Single item request contract for inventory validation (Phase 177)."""

    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    requested_quantity: Decimal = Field(
        ..., gt=0.0, description="Requested purchase quantity (> 0)"
    )  # noqa: E501


class InventoryValidationResult(BaseModel):
    """Validation result entry for a single product request (Phase 177)."""

    model_config = ConfigDict(extra="forbid")

    valid: bool = Field(..., description="True if requested quantity is valid and available")
    product_id: uuid.UUID = Field(..., description="Target Product UUID")
    requested_quantity: Decimal = Field(..., description="Requested purchase quantity")
    available_quantity: Decimal = Field(..., description="Currently available quantity in stock")
    reason: str = Field(
        ...,
        description="Validation result reason (VALID, PRODUCT_NOT_FOUND, PRODUCT_INACTIVE, INSUFFICIENT_STOCK, INVENTORY_UNKNOWN, INVALID_QUANTITY)",  # noqa: E501
    )


class InventoryValidationResponse(BaseModel):
    """Response payload for inventory validation (Phase 177)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    all_valid: bool = Field(..., description="True if all requested items are valid")
    results: list[InventoryValidationResult] = Field(
        default_factory=list, description="Validation results per product item"
    )
