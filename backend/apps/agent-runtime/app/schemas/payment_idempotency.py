"""Pydantic Schemas for Payment Idempotency Subsystem (Phase 297)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IdempotencyState(StrEnum):
    """Lifecycle States for Payment Idempotency Execution (Phase 297)."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class PaymentIdempotencyRecord(BaseModel):
    """Authoritative Payment Idempotency Record Contract (Phase 297).

    Binds idempotency identity to: tenant_id | agent_id | transaction_id | operation | key.
    Distinguishes SAME KEY + SAME REQUEST from SAME KEY + DIFFERENT REQUEST via request_fingerprint.
    Strictly excludes plaintext credentials or secrets.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    record_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique idempotency record UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID context")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID context")
    transaction_id: str = Field(..., description="Authoritative transaction ID context")
    operation: str = Field(..., description="Payment operation name (e.g. create_payment_order)")
    idempotency_key: str = Field(..., description="Client or caller idempotency key string")

    idempotency_identity_hash: str = Field(
        ..., description="SHA-256 hash over canonical tenant|agent|tx|operation|key identity"
    )
    request_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint over canonical request parameters"
    )

    state: IdempotencyState = Field(
        ..., description="Authoritative idempotency state (IN_PROGRESS, COMPLETED, FAILED)"
    )
    safe_result_payload: dict[str, Any] | None = Field(
        default=None, description="Safe serialized result payload (NO secrets)"
    )
    error_code: str | None = Field(default=None, description="Safe error code if operation failed")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Idempotency record creation timestamp UTC",
    )
    completed_at: datetime | None = Field(
        default=None, description="Idempotency operation completion timestamp UTC"
    )
