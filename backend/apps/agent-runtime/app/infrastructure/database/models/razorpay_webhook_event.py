"""RazorpayWebhookEvent ORM model module for AGENTPAY (Phase 064)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.payment_order import PaymentOrder
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction


class RazorpayWebhookEvent(Base):
    """RazorpayWebhookEvent ORM entity representing inbound Razorpay webhooks in AGENTPAY."""

    __tablename__ = "razorpay_webhook_events"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "provider_event_id",
            name="uq_razorpay_webhook_events_tenant_provider_event",
        ),
        UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_razorpay_webhook_events_tenant_event_reference",
        ),
        CheckConstraint(
            "processing_status IN ('received', 'processing', 'processed', 'failed', 'ignored')",
            name="status",
        ),
        CheckConstraint(
            "verification_status IN ('pending', 'verified', 'failed', 'skipped')",
            name="verification_status",
        ),
        Index("ix_razorpay_webhook_events_tenant_id", "tenant_id"),
        Index("ix_razorpay_webhook_events_provider_event_id", "provider_event_id"),
        Index("ix_razorpay_webhook_events_event_reference", "event_reference"),
        Index("ix_razorpay_webhook_events_event_type", "event_type"),
        Index("ix_razorpay_webhook_events_processing_status", "processing_status"),
        Index("ix_razorpay_webhook_events_verification_status", "verification_status"),
        Index("ix_razorpay_webhook_events_payment_order_id", "payment_order_id"),
        Index("ix_razorpay_webhook_events_payment_transaction_id", "payment_transaction_id"),
        Index("ix_razorpay_webhook_events_merchant_id", "merchant_id"),
        Index("ix_razorpay_webhook_events_request_id", "request_id"),
        Index("ix_razorpay_webhook_events_received_at", "received_at"),
    )

    # Primary Key (UUIDv7)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Multi-tenancy isolation key
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Optional Foreign Keys (All ON DELETE RESTRICT)
    payment_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_orders.id",
            name="fk_razorpay_webhook_events_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_razorpay_webhook_events_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_razorpay_webhook_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Provider Identity & References
    provider_event_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Lifecycle & Verification Status
    processing_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="received",
    )
    verification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )
    signature_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Untrusted External Payload Storage & Correlation Context (NO SECRETS)
    event_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    processing_error: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Processing Timestamps
    received_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ORM Relationships
    payment_order: Mapped[Optional["PaymentOrder"]] = relationship("PaymentOrder")
    payment_transaction: Mapped[Optional["PaymentTransaction"]] = relationship("PaymentTransaction")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")

    def __repr__(self) -> str:
        """Return safe string representation excluding untrusted event_payload."""
        return (
            f"<RazorpayWebhookEvent id={self.id} tenant_id={self.tenant_id} "
            f"provider_event_id='{self.provider_event_id}' type='{self.event_type}' "
            f"status='{self.processing_status}' verified={self.signature_verified}>"
        )
