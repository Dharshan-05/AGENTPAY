"""Inventory ORM model module for AGENTPAY (Phase 044)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.product import Product


class Inventory(Base):
    """Inventory ORM entity representing product stock state in AGENTPAY."""

    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", name="uq_inventory_tenant_id_product_id"),
        CheckConstraint("quantity >= 0", name="quantity_nonnegative"),
        CheckConstraint("reserved_quantity >= 0", name="reserved_quantity_nonnegative"),
        CheckConstraint("available_quantity >= 0", name="available_quantity_nonnegative"),
        CheckConstraint("reorder_level >= 0", name="reorder_level_nonnegative"),
        CheckConstraint(
            "reserved_quantity <= quantity AND available_quantity <= quantity AND "
            "available_quantity + reserved_quantity <= quantity",
            name="quantity_consistency",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'discontinued')",
            name="status",
        ),
        Index("ix_inventory_tenant_id", "tenant_id"),
        Index("ix_inventory_merchant_id", "merchant_id"),
        Index("ix_inventory_product_id", "product_id"),
        Index("ix_inventory_status", "status"),
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
            name="fk_inventory_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_inventory_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Stock quantities (NUMERIC precision 18,3 - NEVER float)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )
    available_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )

    # Reorder parameter
    reorder_level: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )

    # Inventory status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
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
            f"<Inventory id={self.id} tenant_id={self.tenant_id} "
            f"product_id={self.product_id} status='{self.status}'>"
        )
