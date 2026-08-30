"""Pydantic Transport & Domain Schemas for Intent Matching Engine (Phase 198)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.intent_verification import DeclaredIntent


class IntentMatchSignal(BaseModel):
    """Signal comparison outcome per intent dimension (Phase 198)."""

    model_config = ConfigDict(extra="forbid")

    dimension: str = Field(
        ..., description="Dimension identifier (action, amount, currency, merchant, etc.)"
    )
    status: str = Field(
        ...,
        description="Signal status (EXACT_MATCH, PARTIAL_MATCH, MISMATCH, MISSING, NOT_APPLICABLE)",  # noqa: E501
    )
    weight: Decimal = Field(..., description="Signal weight component (Decimal)")
    score: Decimal = Field(..., description="Signal contribution score (0.00 to 1.00)")
    detail: str = Field(..., description="Signal comparison detail explanation")


class IntentMatchRequest(BaseModel):
    """Payload contract for intent matching (Phase 198)."""

    model_config = ConfigDict(extra="forbid")

    declared_intent: DeclaredIntent = Field(..., description="Declared buyer/agent intent")
    requested_action: str = Field(..., description="Requested operation action name")
    requested_amount: Decimal | None = Field(default=None, description="Requested operation amount")
    requested_currency: str = Field(default="USD", description="Requested transaction currency")
    requested_merchant_id: str | None = Field(
        default=None, description="Requested Merchant ID/slug"
    )  # noqa: E501
    requested_product_id: str | None = Field(default=None, description="Requested Product ID/sku")
    requested_category: str | None = Field(default=None, description="Requested category")


class IntentMatchResult(BaseModel):
    """Structured outcome of intent matching engine (Phase 198)."""

    model_config = ConfigDict(extra="forbid")

    overall_match: str = Field(
        ..., description="Overall match status (EXACT_MATCH, PARTIAL_MATCH, MISMATCH)"
    )
    match_score: Decimal = Field(
        ..., description="Weighted match score (0.00 to 1.00 Decimal precision)"
    )
    signals: list[IntentMatchSignal] = Field(
        default_factory=list, description="Per-dimension match signal breakdown"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Matching completion timestamp"
    )
