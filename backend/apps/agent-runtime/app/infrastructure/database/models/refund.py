"""Refund ORM model module for AGENTPAY (Phase 065)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.payment_order import PaymentOrder
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction


class Refund(Base):
    """Refund ORM entity representing financial reversal of captured payments in AGENTPAY."""

    __tablename__ = "refunds"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "refund_reference",
            name="uq_refunds_tenant_id_refund_reference",
        ),
        CheckConstraint(
            "refund_type IN ('full', 'partial')",
            name="type",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "amount > 0",
            name="amount_positive",
        ),
        Index("ix_refunds_tenant_id", "tenant_id"),
        Index("ix_refunds_payment_transaction_id", "payment_transaction_id"),
        Index("ix_refunds_payment_order_id", "payment_order_id"),
        Index("ix_refunds_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_refunds_merchant_id", "merchant_id"),
        Index("ix_refunds_refund_reference", "refund_reference"),
        Index("ix_refunds_external_reference", "external_reference"),
        Index("ix_refunds_provider_refund_reference", "provider_refund_reference"),
        Index("ix_refunds_refund_type", "refund_type"),
        Index("ix_refunds_status", "status"),
        Index("ix_refunds_requested_at", "requested_at"),
        Index("ix_refunds_created_at", "created_at"),
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

    # Required Relationship to PaymentTransaction (ON DELETE RESTRICT)
    payment_transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_refunds_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Optional Foreign Keys (All ON DELETE RESTRICT)
    payment_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_orders.id",
            name="fk_refunds_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_refunds_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_refunds_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Provider References (NON-SECRET)
    refund_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    provider_refund_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Classification & Status
    refund_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="full",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    # Financial Precision (NUMERIC 18,4 Decimal ONLY)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Reason & Non-secret JSONB Metadata
    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    refund_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Lifecycle Timestamps & Soft Delete
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
    cancelled_at: Mapped[datetime | None] = mapped_column(
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # ORM Relationships
    payment_transaction: Mapped["PaymentTransaction"] = relationship("PaymentTransaction")
    payment_order: Mapped[Optional["PaymentOrder"]] = relationship("PaymentOrder")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )

    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING refund_metadata and secrets."""
        return (
            f"<Refund id={self.id} tenant_id={self.tenant_id} "
            f"transaction_id={self.payment_transaction_id} reference='{self.refund_reference}' "
            f"type='{self.refund_type}' status='{self.status}' amount={self.amount}>"
        )
