"""Pydantic Transport Schemas for AgentPay Core Adapter (Phase 160)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requests import StrictRequestModel


class AgentPayTransactionRequest(StrictRequestModel):
    """Financial transaction initiation request contract (Phase 160)."""

    amount: float = Field(..., gt=0.0, description="Transaction amount")
    currency: str = Field(default="USD", max_length=10, description="Currency code")
    recipient: str = Field(
        ..., min_length=2, max_length=150, description="Payment recipient/merchant name"
    )  # noqa: E501
    description: str = Field(
        ..., min_length=3, max_length=255, description="Transaction description"
    )  # noqa: E501
    idempotency_key: str = Field(
        ..., min_length=8, max_length=128, description="Mandatory financial idempotency key"
    )
    correlation_id: str | None = Field(
        default=None, max_length=100, description="Correlation tracing ID"
    )  # noqa: E501
    metadata: dict[str, Any] = Field(default_factory=dict, description="Transaction metadata")


class AgentPayTransactionResult(BaseModel):
    """Financial transaction result contract (Phase 160)."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: uuid.UUID = Field(..., description="Unique transaction UUID")
    reference_code: str = Field(..., description="Human-readable transaction reference")
    status: str = Field(
        ..., description="Transaction status (SETTLED, PENDING_APPROVAL, PENDING, FAILED)"
    )  # noqa: E501
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code")
    recipient: str = Field(..., description="Recipient merchant")
    requires_approval: bool = Field(..., description="True if transaction pending human approval")
    approval_request_id: uuid.UUID | None = Field(
        default=None, description="Approval request UUID if pending"
    )  # noqa: E501
    idempotency_key: str = Field(..., description="Idempotency key")
    retry_safety: str = Field(
        default="SAFE_TO_RETRY", description="Phase 163 retry safety classification"
    )  # noqa: E501
    executed_at: datetime = Field(..., description="Execution completion timestamp")
