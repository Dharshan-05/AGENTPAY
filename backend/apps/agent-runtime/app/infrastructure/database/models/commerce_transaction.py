"""CommerceTransaction ORM model module for AGENTPAY (Phase 049)."""

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
    from app.infrastructure.database.models.commerce_event import CommerceEvent
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan


class CommerceTransaction(Base):
    """CommerceTransaction ORM entity representing financial commerce transactions in AGENTPAY."""

    __tablename__ = "commerce_transactions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "transaction_reference",
            name="uq_commerce_transactions_tenant_id_transaction_reference",
        ),
        CheckConstraint(
            "transaction_type IN ('purchase', 'authorization', 'capture', "
            "'refund', 'void', 'adjustment')",
            name="transaction_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'authorized', 'completed', 'failed', "
            "'cancelled', 'refunded', 'partially_refunded')",
            name="status",
        ),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("amount >= 0", name="amount_nonnegative"),
        CheckConstraint("subtotal >= 0", name="subtotal_nonnegative"),
        CheckConstraint("tax_amount >= 0", name="tax_nonnegative"),
        CheckConstraint("discount_amount >= 0", name="discount_nonnegative"),
        CheckConstraint("fee_amount >= 0", name="fee_nonnegative"),
        CheckConstraint("total_amount >= 0", name="total_nonnegative"),
        CheckConstraint("refunded_amount >= 0", name="refunded_nonnegative"),
        CheckConstraint(
            "refunded_amount <= total_amount",
            name="refund_bounds",
        ),
        Index("ix_commerce_transactions_tenant_id", "tenant_id"),
        Index("ix_commerce_transactions_merchant_id", "merchant_id"),
        Index("ix_commerce_transactions_agent_id", "agent_id"),
        Index("ix_commerce_transactions_product_id", "product_id"),
        Index("ix_commerce_transactions_offer_id", "offer_id"),
        Index("ix_commerce_transactions_purchase_intent_id", "purchase_intent_id"),
        Index("ix_commerce_transactions_purchase_plan_id", "purchase_plan_id"),
        Index("ix_commerce_transactions_external_reference", "external_reference"),
        Index("ix_commerce_transactions_transaction_type", "transaction_type"),
        Index("ix_commerce_transactions_status", "status"),
    )

    # Primary key: UUID (UUIDv7)
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

    # Foreign keys
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_commerce_transactions_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_commerce_transactions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_commerce_transactions_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_commerce_transactions_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_ctxns_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_ctxns_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Transaction References & Identity
    transaction_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    # Quantity & Financial Fields (NUMERIC precision 18,3 and 18,4 - NEVER float)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("1.000"),
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    refunded_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Non-secret Payment Provider References
    payment_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    provider_transaction_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    provider_authorization_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Metadata Payload (JSONB, zero secrets)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Lifecycle Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    authorized_at: Mapped[datetime | None] = mapped_column(
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
    refunded_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # ORM Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant")
    agent: Mapped["Agent"] = relationship("Agent")
    product: Mapped["Product"] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    commerce_events: Mapped[list["CommerceEvent"]] = relationship(
        "CommerceEvent",
        back_populates="transaction",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<CommerceTransaction id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.transaction_reference}' type='{self.transaction_type}' "
            f"status='{self.status}' total_amount={self.total_amount}>"
        )
