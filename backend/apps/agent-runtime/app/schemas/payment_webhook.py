"""Pydantic Schemas for Razorpay Webhook Ingestion & Signature Verification (Phase 293–294)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookIngestionOutcome(StrEnum):
    """Outcome enum for Webhook Ingestion Boundary (Phase 293)."""

    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    MALFORMED_PAYLOAD = "MALFORMED_PAYLOAD"
    REJECTED = "REJECTED"


class UntrustedWebhookRequest(BaseModel):
    """Untrusted raw webhook payload input boundary (Phase 293).

    Holds exact raw body bytes and signature header prior to cryptographic verification.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    raw_body: bytes = Field(..., description="Exact raw HTTP request body bytes")
    signature: str = Field(..., description="Razorpay HMAC signature header string")
    tenant_id: uuid.UUID | None = Field(
        default=None, description="Optional tenant UUID context from header"
    )
    environment: str | None = Field(default=None, description="Optional environment context")
    provider_name: str = Field(default="razorpay", description="Payment provider name")


class WebhookSignatureVerificationResult(BaseModel):
    """Cryptographic signature verification outcome contract (Phase 294).

    Strictly excludes key_secret or webhook_secret.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    verified: bool = Field(..., description="True ONLY when HMAC-SHA256 signature is valid")
    provider: str = Field(default="razorpay", description="Payment provider name")
    algorithm: str = Field(default="HMAC-SHA256", description="Signature algorithm string")
    verification_status: str = Field(
        ..., description="Status string: VERIFIED, INVALID_SIGNATURE, MISSING_SECRET, ERROR"
    )
    reason_code: str = Field(..., description="Structured verification rationale")
    payload_fingerprint: str = Field(
        ..., description="SHA-256 digest over exact raw request body bytes"
    )
    verified_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Signature verification timestamp UTC",
    )


class VerifiedWebhookEnvelope(BaseModel):
    """Trusted webhook envelope created ONLY after successful signature verification (Phase 293)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    envelope_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique trusted envelope UUID"
    )
    provider: str = Field(default="razorpay", description="Payment provider name")
    event_id: str | None = Field(
        default=None, description="Provider event ID (e.g., event_123) if present"
    )
    event_type: str = Field(
        ..., description="Razorpay event type string (e.g., payment.authorized)"
    )
    tenant_id: uuid.UUID | None = Field(
        default=None, description="Bound tenant UUID context if resolved"
    )
    environment: str = Field(..., description="Target environment string (e.g., test, production)")
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Webhook received timestamp UTC",
    )
    verification_status: str = Field(default="VERIFIED", description="Verification status string")
    signature_algorithm: str = Field(
        default="HMAC-SHA256", description="Signature algorithm string"
    )
    payload_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over raw body bytes"
    )
    raw_payload_digest: str = Field(..., description="SHA-256 digest over exact raw body bytes")
    verified: bool = Field(default=True, description="Always True for VerifiedWebhookEnvelope")
    payload: dict[str, Any] = Field(
        ..., description="Safe parsed JSON payload object (parsed ONLY post-verification)"
    )


class WebhookIngestionResult(BaseModel):
    """Safe acknowledgement response returned by Webhook API (Phase 293)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    ingestion_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique webhook ingestion UUID"
    )
    outcome: WebhookIngestionOutcome = Field(..., description="Ingestion outcome enum")
    status_code: int = Field(..., description="HTTP status code integer")
    message: str = Field(..., description="Safe user-facing result summary message")
    event_id: str | None = Field(default=None, description="Provider event ID if available")
    event_type: str | None = Field(default=None, description="Provider event type if available")
    payload_fingerprint: str | None = Field(
        default=None, description="SHA-256 fingerprint over raw payload"
    )
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Ingestion timestamp UTC",
    )
