"""PurchaseIntent ORM model module for AGENTPAY (Phase 047)."""

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
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_plan import PurchasePlan


class PurchaseIntent(Base):
    """PurchaseIntent ORM entity representing declared buyer purchase intent in AGENTPAY."""

    __tablename__ = "purchase_intents"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "intent_reference",
            name="uq_purchase_intents_tenant_id_intent_reference",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired', 'cancelled')",
            name="status",
        ),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_nonnegative"),
        CheckConstraint("total_amount >= 0", name="total_amount_nonnegative"),
        CheckConstraint(
            "expires_at IS NULL OR requested_at <= expires_at",
            name="date_bounds",
        ),
        Index("ix_purchase_intents_tenant_id", "tenant_id"),
        Index("ix_purchase_intents_merchant_id", "merchant_id"),
        Index("ix_purchase_intents_agent_id", "agent_id"),
        Index("ix_purchase_intents_product_id", "product_id"),
        Index("ix_purchase_intents_offer_id", "offer_id"),
        Index("ix_purchase_intents_status", "status"),
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
            name="fk_purchase_intents_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_purchase_intents_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_purchase_intents_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_purchase_intents_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Reference
    intent_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    # Quantities & Pricing (NUMERIC precision 18,3 and 18,4 - NEVER float)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("1.000"),
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
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

    # Temporal validity
    requested_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Request context
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    actor_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Metadata payload (JSONB, zero secrets)
    intent_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Timestamps & Soft Delete
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
    merchant: Mapped["Merchant"] = relationship("Merchant")
    agent: Mapped["Agent"] = relationship("Agent")
    product: Mapped["Product"] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_plans: Mapped[list["PurchasePlan"]] = relationship(
        "PurchasePlan",
        back_populates="purchase_intent",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<PurchaseIntent id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.intent_reference}' status='{self.status}' "
            f"total_amount={self.total_amount}>"
        )
