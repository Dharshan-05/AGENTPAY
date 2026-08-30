"""PaymentOrder ORM model module for AGENTPAY (Phase 061)."""

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
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.payment_event import PaymentEvent
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan


class PaymentOrder(Base):
    """PaymentOrder ORM entity representing financial payment order boundaries in AGENTPAY."""

    __tablename__ = "payment_orders"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "order_reference",
            name="uq_payment_orders_tenant_id_order_reference",
        ),
        CheckConstraint(
            "status IN ('created', 'pending', 'processing', 'authorized', "
            "'completed', 'failed', 'cancelled', 'expired')",
            name="status",
        ),
        CheckConstraint(
            "amount >= 0",
            name="amount_nonnegative",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="subtotal_nonnegative",
        ),
        CheckConstraint(
            "tax_amount >= 0",
            name="tax_nonnegative",
        ),
        CheckConstraint(
            "discount_amount >= 0",
            name="discount_nonnegative",
        ),
        CheckConstraint(
            "fee_amount >= 0",
            name="fee_nonnegative",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="total_nonnegative",
        ),
        CheckConstraint(
            "quantity IS NULL OR quantity >= 0",
            name="quantity_nonnegative",
        ),
        CheckConstraint(
            "(authorized_at IS NULL OR authorized_at >= created_at) AND "
            "(completed_at IS NULL OR completed_at >= created_at)",
            name="date_bounds",
        ),
        Index("ix_payment_orders_tenant_id", "tenant_id"),
        Index("ix_payment_orders_merchant_id", "merchant_id"),
        Index("ix_payment_orders_agent_id", "agent_id"),
        Index("ix_payment_orders_product_id", "product_id"),
        Index("ix_payment_orders_offer_id", "offer_id"),
        Index("ix_payment_orders_purchase_intent_id", "purchase_intent_id"),
        Index("ix_payment_orders_purchase_plan_id", "purchase_plan_id"),
        Index("ix_payment_orders_order_reference", "order_reference"),
        Index("ix_payment_orders_external_reference", "external_reference"),
        Index("ix_payment_orders_status", "status"),
        Index("ix_payment_orders_tenant_status", "tenant_id", "status"),
        Index("ix_payment_orders_created_at", "created_at"),
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

    # Foreign Keys (All ON DELETE RESTRICT)
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_payment_orders_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_payment_orders_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_payment_orders_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_payment_orders_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_payment_orders_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_payment_orders_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Status
    order_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="created",
    )

    # Financial Amounts (NUMERIC 18,4 Decimal)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
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
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Quantity (NUMERIC 18,3 Decimal)
    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 3),
        nullable=True,
        default=Decimal("1.000"),
    )

    # Non-secret JSONB Metadata
    order_metadata: Mapped[dict[str, Any] | None] = mapped_column(
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
    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # ORM Relationships
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    product: Mapped[Optional["Product"]] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    payment_transactions: Mapped[list["PaymentTransaction"]] = relationship(
        "PaymentTransaction",
        back_populates="payment_order",
    )
    payment_events: Mapped[list["PaymentEvent"]] = relationship(
        "PaymentEvent",
        back_populates="payment_order",
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding JSONB metadata."""
        return (
            f"<PaymentOrder id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.order_reference}' total='{self.total_amount}' "
            f"currency='{self.currency_code}' status='{self.status}'>"
        )
