"""Pydantic Transport & Service Contracts for Payment Service (Phase 288)."""

from __future__ import annotations

import math
import re
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

IDEMPOTENCY_KEY_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+$")
PROHIBITED_PAYMENT_SERVICE_KEYS = {
    "final_decision",
    "decision",
    "risk_score",
    "score",
    "override",
    "razorpay_order_id",
    "payment_id",
    "checkout_session",
    "is_fraud",
    "fraud_label",
}


class SupportedCurrency(StrEnum):
    """Supported ISO 4217 Currency Codes (Phase 288)."""

    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    SGD = "SGD"


class PaymentServiceOutcome(StrEnum):
    """Authoritative Payment Service Outcome Enum (Phase 288)."""

    AUTHORIZED_FOR_PAYMENT = "AUTHORIZED_FOR_PAYMENT"
    SUSPENDED_FOR_APPROVAL = "SUSPENDED_FOR_APPROVAL"
    DENIED = "DENIED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class PaymentServiceRequest(BaseModel):
    """Input payload for Payment Service evaluation (Phase 288)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    amount: Decimal = Field(..., description="Financial payment amount (Decimal)")
    currency: SupportedCurrency = Field(..., description="Explicit ISO currency code")
    idempotency_key: str = Field(
        ..., description="Deterministic idempotency key for payment request deduplication"
    )
    payment_reference: str | None = Field(
        default=None, description="Optional payment reference or intent ID binding"
    )
    provider_name: str = Field(
        default="razorpay", description="Target payment provider name string"
    )
    context_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary context metadata"
    )

    @field_validator("amount")
    @classmethod
    def validate_financial_amount(cls, v: Decimal) -> Decimal:
        """Validate monetary amount is positive, non-zero, finite, and bounded."""
        if not isinstance(v, Decimal):
            raise ValueError("Payment amount must be a Decimal instance.")

        # Check for NaN or Infinity
        float_val = float(v)
        if math.isnan(float_val) or math.isinf(float_val):
            raise ValueError("Payment amount cannot be NaN or Infinity.")

        if v <= Decimal("0"):
            raise ValueError("Payment amount must be strictly greater than 0.")

        if v > Decimal("1000000.00"):
            raise ValueError("Payment amount exceeds maximum transaction limit of 1,000,000.00.")

        return v

    @field_validator("idempotency_key")
    @classmethod
    def validate_idempotency_key(cls, v: str) -> str:
        """Validate non-empty, bounded, safe character idempotency key."""
        clean = v.strip()
        if not clean:
            raise ValueError("Idempotency key cannot be empty.")
        if len(clean) < 8 or len(clean) > 128:
            raise ValueError("Idempotency key length must be between 8 and 128 characters.")
        if not IDEMPOTENCY_KEY_REGEX.match(clean):
            raise ValueError(
                "Idempotency key contains invalid characters. "
                "Allowed: alphanumeric, dashes, underscores."
            )
        return clean

    @field_validator("context_metadata")
    @classmethod
    def validate_no_prohibited_overrides_or_leakage(cls, value: dict[str, Any]) -> dict[str, Any]:
        """Reject client-supplied decision forgery or target leakage payloads."""
        for k in value:
            if k.lower() in PROHIBITED_PAYMENT_SERVICE_KEYS:
                raise ValueError(
                    f"Prohibited metadata key '{k}' detected in payment service request."
                )
        return value


class PaymentServiceResult(BaseModel):
    """Immutable Outcome Contract produced by Payment Service (Phase 288)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    service_run_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique payment service run UUID"
    )
    authorization_id: uuid.UUID | None = Field(
        default=None, description="Payment authorization run UUID if evaluated"
    )
    decision_id: uuid.UUID | None = Field(default=None, description="Authoritative decision UUID")
    evaluation_id: uuid.UUID | None = Field(
        default=None, description="Authoritative risk evaluation run UUID"
    )

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    amount: Decimal = Field(..., description="Monetary payment amount (Decimal)")
    currency: SupportedCurrency = Field(..., description="Explicit ISO currency code")
    idempotency_key: str = Field(..., description="Idempotency key")

    outcome: PaymentServiceOutcome = Field(..., description="Enforced payment service outcome enum")
    reason_code: str = Field(..., description="Structured service reason code")
    decision_reason: str | None = Field(
        default=None, description="Preserved upstream decision reason code string"
    )
    provider_name: str = Field(..., description="Payment provider name")
    authorization_fingerprint: str | None = Field(
        default=None, description="SHA-256 payment authorization fingerprint if evaluated"
    )

    payment_id: str | None = Field(
        default=None, description="Actual payment ID (Must remain None in Phase 288)"
    )
    order_id: str | None = Field(
        default=None, description="Actual order ID (Must remain None in Phase 288)"
    )

    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Payment service evaluation timestamp UTC",
    )


def amount_to_minor_units(amount: Decimal, currency: SupportedCurrency) -> int:
    """Safely convert Decimal monetary amount to provider minor units (e.g. Paise/Cents).

    Uses exact Decimal arithmetic without float casting.
    """
    if not isinstance(amount, Decimal):
        raise ValueError("Monetary amount must be a Decimal instance.")

    float_val = float(amount)
    if math.isnan(float_val) or math.isinf(float_val):
        raise ValueError("Monetary amount cannot be NaN or Infinity.")

    if amount <= Decimal("0"):
        raise ValueError("Monetary amount must be strictly greater than 0.")

    # Standard ISO 4217 currencies in SupportedCurrency all use 2 decimal places (100 minor units)
    multiplier = Decimal("100")
    scaled = amount * multiplier

    if scaled != scaled.quantize(Decimal("1")):
        raise ValueError(
            "Monetary amount has fractional minor units beyond provider currency precision."
        )

    return int(scaled)


class PaymentOrderRequest(BaseModel):
    """Provider-neutral order creation request contract (Phase 289)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    amount: Decimal = Field(..., description="Financial payment amount (Decimal)")
    currency: SupportedCurrency = Field(..., description="Explicit ISO currency code")
    idempotency_key: str = Field(..., description="Deterministic idempotency key")
    receipt: str | None = Field(default=None, description="Safe receipt reference identifier")
    notes: dict[str, str] = Field(default_factory=dict, description="Safe metadata notes map")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate Decimal monetary amount."""
        if not isinstance(v, Decimal):
            raise ValueError("Payment amount must be a Decimal instance.")
        float_val = float(v)
        if math.isnan(float_val) or math.isinf(float_val):
            raise ValueError("Payment amount cannot be NaN or Infinity.")
        if v <= Decimal("0"):
            raise ValueError("Payment amount must be strictly greater than 0.")
        if v > Decimal("1000000.00"):
            raise ValueError("Payment amount exceeds maximum transaction limit.")
        return v


class PaymentOrderResult(BaseModel):
    """Normalized safe Razorpay order result contract (Phase 289)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    order_id: str = Field(..., description="Real Razorpay provider order ID")
    provider_name: str = Field(default="razorpay", description="Payment provider name")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    amount: Decimal = Field(..., description="Financial payment amount (Decimal)")
    amount_minor_units: int = Field(..., description="Amount in minor units (Paise/Cents)")
    currency: SupportedCurrency = Field(..., description="Explicit ISO currency code")
    status: str = Field(default="created", description="Razorpay order status string")
    idempotency_key: str = Field(..., description="Preserved idempotency key")
    authorization_id: uuid.UUID = Field(..., description="Authoritative payment authorization UUID")
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 payment authorization fingerprint"
    )

    payment_success: bool = Field(
        default=False, description="Must remain False in Phase 289 (No payment verification)"
    )
    payment_verified: bool = Field(
        default=False, description="Must remain False in Phase 289 (No payment verification)"
    )
    captured: bool = Field(
        default=False, description="Must remain False in Phase 289 (No payment capture)"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Order creation timestamp UTC",
    )

    @field_validator("order_id")
    @classmethod
    def validate_order_id_non_empty(cls, v: str) -> str:
        """Validate non-empty order_id string."""
        clean = v.strip() if v else ""
        if not clean:
            raise ValueError("Order ID cannot be empty or blank.")
        return clean


class RazorpayCheckoutConfig(BaseModel):
    """Safe frontend-facing Razorpay Checkout configuration (Phase 290).

    Exposes public key_id to the browser, while key_secret remains strictly server-side.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    key_id: str = Field(..., description="Public Razorpay Key ID (Safe for frontend exposure)")
    order_id: str = Field(..., description="Real Razorpay provider order ID")
    amount: Decimal = Field(..., description="Financial payment amount (Decimal)")
    amount_minor_units: int = Field(..., description="Amount in minor units (Paise/Cents)")
    currency: SupportedCurrency = Field(..., description="Explicit ISO currency code")
    name: str = Field(default="AGENTPAY", description="Merchant display name for checkout modal")
    description: str = Field(..., description="Safe description for checkout modal")
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")

    checkout_status: str = Field(
        default="CHECKOUT_READY", description="Safe checkout status string"
    )
    payment_success: bool = Field(
        default=False, description="Must remain False in Phase 290 (No payment verification)"
    )
    payment_verified: bool = Field(
        default=False, description="Must remain False in Phase 290 (No payment verification)"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Checkout configuration timestamp UTC",
    )


class PaymentVerificationStatus(StrEnum):
    """Authoritative Payment Verification Status Enum (Phase 291)."""

    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    MISMATCH = "MISMATCH"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    INVALID_PAYMENT = "INVALID_PAYMENT"
    INVALID_ORDER = "INVALID_ORDER"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    ALREADY_VERIFIED = "ALREADY_VERIFIED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class PaymentVerificationRequest(BaseModel):
    """Input payload for payment verification (Phase 291)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    order_id: str = Field(..., description="Razorpay order ID")
    payment_id: str = Field(..., description="Razorpay payment ID returned by checkout")
    signature: str = Field(..., description="Razorpay HMAC-SHA256 signature returned by checkout")
    amount: Decimal = Field(..., description="Expected monetary amount")
    currency: SupportedCurrency = Field(..., description="Expected ISO currency code")
    authorization_id: uuid.UUID = Field(..., description="Authoritative payment authorization UUID")
    authorization_fingerprint: str = Field(
        ..., description="SHA-256 payment authorization fingerprint"
    )
    idempotency_key: str = Field(..., description="Idempotency key")

    @field_validator("signature", "payment_id", "order_id")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validate non-empty strings."""
        clean = v.strip() if v else ""
        if not clean:
            raise ValueError("Field cannot be empty or blank.")
        return clean


class PaymentVerificationResult(BaseModel):
    """Normalized safe payment verification result contract (Phase 291)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    verification_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique verification run UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    order_id: str = Field(..., description="Razorpay order ID")
    payment_id: str = Field(..., description="Razorpay payment ID")
    status: PaymentVerificationStatus = Field(..., description="Authoritative verification status")
    reason_code: str = Field(..., description="Structured verification reason code")
    amount: Decimal = Field(..., description="Verified monetary amount")
    currency: SupportedCurrency = Field(..., description="Verified ISO currency code")

    payment_success: bool = Field(
        ..., description="True ONLY when cryptographic & contextual verification succeeds"
    )
    payment_verified: bool = Field(
        ..., description="True ONLY when cryptographic & contextual verification succeeds"
    )
    captured: bool = Field(
        default=False, description="Must remain False in Phase 291 (No payment capture)"
    )

    verification_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical safe metadata"
    )
    verified_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Verification completion timestamp UTC",
    )


class PaymentStatus(StrEnum):
    """Authoritative Payment Lifecycle State Machine Enum (Phase 292)."""

    CREATED = "CREATED"
    ORDER_CREATED = "ORDER_CREATED"
    CHECKOUT_READY = "CHECKOUT_READY"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_VERIFIED = "PAYMENT_VERIFIED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    UNKNOWN = "UNKNOWN"


class PaymentStatusTransitionRecord(BaseModel):
    """Immutable transition record for payment state machine (Phase 292)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    record_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique state transition record UUID"
    )
    tenant_id: uuid.UUID = Field(..., description="Authoritative tenant UUID")
    agent_id: uuid.UUID = Field(..., description="Authoritative agent UUID")
    transaction_id: str = Field(..., description="Authoritative transaction ID")
    order_id: str = Field(..., description="Razorpay order ID")
    payment_id: str | None = Field(default=None, description="Razorpay payment ID if available")

    previous_status: PaymentStatus = Field(..., description="Source state before transition")
    new_status: PaymentStatus = Field(..., description="Target state after transition")
    transition_reason: str = Field(..., description="Structured transition rationale")
    transition_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="State transition timestamp UTC",
    )
    verification_fingerprint: str | None = Field(
        default=None, description="Payment verification fingerprint if applicable"
    )
    transition_fingerprint: str = Field(
        ..., description="SHA-256 fingerprint calculated over canonical transition metadata"
    )
