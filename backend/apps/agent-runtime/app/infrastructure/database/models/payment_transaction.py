"""PaymentTransaction ORM model module for AGENTPAY (Phase 062)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.payment_event import PaymentEvent
    from app.infrastructure.database.models.payment_order import PaymentOrder


class PaymentTransaction(Base):
    """PaymentTransaction ORM entity representing payment-processing attempts in AGENTPAY."""

    __tablename__ = "payment_transactions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "transaction_reference",
            name="uq_payment_transactions_tenant_id_transaction_reference",
        ),
        CheckConstraint(
            "transaction_type IN ('authorization', 'capture', 'payment', "
            "'refund', 'void', 'adjustment')",
            name="transaction_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'authorized', 'completed', 'failed', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "amount >= 0",
            name="amount_nonnegative",
        ),
        CheckConstraint(
            "authorized_amount IS NULL OR authorized_amount >= 0",
            name="authorized_amount_nonnegative",
        ),
        CheckConstraint(
            "captured_amount IS NULL OR captured_amount >= 0",
            name="captured_amount_nonnegative",
        ),
        CheckConstraint(
            "fee_amount >= 0",
            name="fee_amount_nonnegative",
        ),
        CheckConstraint(
            "tax_amount >= 0",
            name="tax_amount_nonnegative",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="total_amount_nonnegative",
        ),
        Index("ix_payment_transactions_tenant_id", "tenant_id"),
        Index("ix_payment_transactions_payment_order_id", "payment_order_id"),
        Index("ix_payment_transactions_merchant_id", "merchant_id"),
        Index("ix_payment_transactions_agent_id", "agent_id"),
        Index("ix_payment_transactions_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_payment_transactions_transaction_reference", "transaction_reference"),
        Index("ix_payment_transactions_external_reference", "external_reference"),
        Index("ix_payment_transactions_payment_provider", "payment_provider"),
        Index(
            "ix_payment_transactions_provider_transaction_reference",
            "provider_transaction_reference",
        ),
        Index("ix_payment_transactions_transaction_type", "transaction_type"),
        Index("ix_payment_transactions_status", "status"),
        Index("ix_payment_transactions_tenant_status", "tenant_id", "status"),
        Index("ix_payment_transactions_created_at", "created_at"),
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

    # Required Relationship to PaymentOrder
    payment_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_orders.id",
            name="fk_payment_transactions_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Optional Foreign Keys (All ON DELETE RESTRICT)
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_payment_transactions_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_payment_transactions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_payment_transactions_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Provider References (NON-SECRET)
    transaction_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    payment_provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    provider_transaction_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    provider_authorization_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Classification & Status
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    # Financial Amounts (NUMERIC 18,4 Decimal)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    authorized_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )
    captured_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )
    fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Non-secret JSONB Metadata
    transaction_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Lifecycle Timestamps & Soft Delete
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    authorized_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    captured_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # ORM Relationships
    payment_order: Mapped["PaymentOrder"] = relationship(
        "PaymentOrder",
        back_populates="payment_transactions",
    )
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )
    payment_events: Mapped[list["PaymentEvent"]] = relationship(
        "PaymentEvent",
        back_populates="payment_transaction",
    )

    def __repr__(self) -> str:
        """Return safe string representation REDACTING transaction_metadata and secrets."""
        return (
            f"<PaymentTransaction id={self.id} tenant_id={self.tenant_id} "
            f"order_id={self.payment_order_id} reference='{self.transaction_reference}' "
            f"provider='{self.payment_provider}' type='{self.transaction_type}' "
            f"status='{self.status}'>"
        )
