"""Offer ORM model module for AGENTPAY (Phase 046)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.product import Product


class Offer(Base):
    """Offer ORM entity representing commercial offers in AGENTPAY."""

    __tablename__ = "offers"

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_offers_tenant_id_slug"),
        CheckConstraint("price >= 0", name="price_nonnegative"),
        CheckConstraint("min_quantity >= 0", name="min_quantity_nonnegative"),
        CheckConstraint(
            "max_quantity IS NULL OR max_quantity >= min_quantity",
            name="max_quantity_bounds",
        ),
        CheckConstraint(
            "starts_at IS NULL OR ends_at IS NULL OR starts_at <= ends_at",
            name="date_bounds",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'expired', 'suspended')",
            name="status",
        ),
        Index("ix_offers_tenant_id", "tenant_id"),
        Index("ix_offers_merchant_id", "merchant_id"),
        Index("ix_offers_product_id", "product_id"),
        Index("ix_offers_status", "status"),
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
            name="fk_offers_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_offers_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Offer identity & slug
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    # Pricing & Currency (NUMERIC precision 18,4 - NEVER float)
    price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Validity Period
    starts_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Quantity boundaries
    min_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("1.000"),
    )
    max_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 3),
        nullable=True,
    )

    # Metadata payload (JSONB, zero secrets)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
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
    product: Mapped["Product"] = relationship("Product")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<Offer id={self.id} tenant_id={self.tenant_id} "
            f"merchant_id={self.merchant_id} product_id={self.product_id} "
            f"slug='{self.slug}' status='{self.status}' price={self.price}>"
        )
