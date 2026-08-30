"""Cancellation ORM model module for AGENTPAY (Phase 066)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.payment_order import PaymentOrder
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction


class Cancellation(Base):
    """Cancellation ORM entity representing order/payment termination actions in AGENTPAY."""

    __tablename__ = "cancellations"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "cancellation_reference",
            name="uq_cancellations_tenant_id_cancellation_reference",
        ),
        CheckConstraint(
            "status IN ('requested', 'processing', 'completed', 'failed', 'rejected')",
            name="status",
        ),
        CheckConstraint(
            "reason_type IN ('customer_request', 'merchant_request', 'payment_timeout', "
            "'duplicate_order', 'system_error', 'risk_rejection', 'other')",
            name="reason_type",
        ),
        Index("ix_cancellations_tenant_id", "tenant_id"),
        Index("ix_cancellations_payment_order_id", "payment_order_id"),
        Index("ix_cancellations_payment_transaction_id", "payment_transaction_id"),
        Index("ix_cancellations_merchant_id", "merchant_id"),
        Index("ix_cancellations_agent_id", "agent_id"),
        Index("ix_cancellations_cancellation_reference", "cancellation_reference"),
        Index(
            "ix_cancellations_provider_cancellation_reference",
            "provider_cancellation_reference",
        ),
        Index("ix_cancellations_status", "status"),
        Index("ix_cancellations_reason_type", "reason_type"),
        Index("ix_cancellations_requested_at", "requested_at"),
        Index("ix_cancellations_created_at", "created_at"),
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
            name="fk_cancellations_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_cancellations_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_cancellations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_cancellations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Provider References (NON-SECRET)
    cancellation_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    provider_cancellation_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Classification & Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="requested",
    )
    reason_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="customer_request",
    )
    reason_detail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Non-secret JSONB Metadata
    cancellation_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Lifecycle Timestamps
    requested_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
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
    agent: Mapped[Optional["Agent"]] = relationship("Agent")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING cancellation_metadata and secrets."""
        return (
            f"<Cancellation id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.cancellation_reference}' reason='{self.reason_type}' "
            f"status='{self.status}'>"
        )
