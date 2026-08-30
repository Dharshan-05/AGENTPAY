"""Pydantic Transport & Domain Schemas for Intent Verification Engine (Phase 197)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DeclaredIntent(BaseModel):
    """Declared buyer/agent intent specification payload contract (Phase 197)."""

    model_config = ConfigDict(extra="forbid")

    intent_id: uuid.UUID | None = Field(default=None, description="Optional intent record UUID")
    action: str = Field(..., description="Declared action (e.g., 'payment', 'purchase', 'pay')")
    amount: Decimal | None = Field(default=None, description="Declared max/exact amount")
    currency: str | None = Field(default="USD", description="Declared ISO currency code")
    merchant_id: uuid.UUID | None = Field(default=None, description="Declared target Merchant UUID")
    merchant_slug: str | None = Field(default=None, description="Declared merchant slug")
    product_id: uuid.UUID | None = Field(default=None, description="Declared target Product UUID")
    category: str | None = Field(default=None, description="Declared target product category")
    quantity: Decimal | None = Field(default=None, description="Declared purchase quantity")


class IntentVerificationRequest(BaseModel):
    """Payload contract for intent verification against requested operation (Phase 197)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    agent_id: uuid.UUID = Field(..., description="Target Agent UUID")
    principal_id: uuid.UUID | None = Field(default=None, description="Authenticated principal UUID")
    declared_intent: DeclaredIntent | None = Field(
        default=None, description="Declared intent payload"
    )
    requested_action: str = Field(..., description="Requested operation action name")
    requested_amount: Decimal | None = Field(default=None, description="Requested operation amount")
    requested_currency: str = Field(default="USD", description="Requested transaction currency")
    requested_merchant_id: uuid.UUID | None = Field(
        default=None, description="Requested Merchant UUID"
    )
    requested_product_id: uuid.UUID | None = Field(
        default=None, description="Requested Product UUID"
    )
    requested_category: str | None = Field(default=None, description="Requested operation category")
    requested_quantity: Decimal | None = Field(
        default=None, description="Requested operation quantity"
    )


class IntentVerificationResult(BaseModel):
    """Structured outcome of evaluating intent verification (Phase 197)."""

    model_config = ConfigDict(extra="forbid")

    verified: bool = Field(..., description="True if intent is verified and consistent")
    decision: str = Field(
        ..., description="Verification outcome (VERIFIED, MISMATCH, INSUFFICIENT, INVALID, DENIED)"
    )
    reason_code: str = Field(..., description="Structured reason code identifier")
    confidence_score: Decimal = Field(
        ..., description="Verification confidence score (0.00 to 1.00 Decimal)"
    )
    explanation: str = Field(..., description="Human-readable decision explanation")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Verification completion timestamp"
    )
