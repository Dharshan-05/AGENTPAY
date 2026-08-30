"""Product ORM model module for AGENTPAY (Phase 042)."""

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


class Product(Base):
    """Product ORM entity representing a product offered by a Merchant in AGENTPAY."""

    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("merchant_id", "sku", name="uq_products_merchant_id_sku"),
        CheckConstraint("price >= 0", name="price_nonnegative"),
        Index("ix_products_tenant_id", "tenant_id"),
        Index("ix_products_merchant_id", "merchant_id"),
        Index("ix_products_status", "status"),
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

    # Merchant relationship
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", name="fk_products_merchant_id_merchants", ondelete="RESTRICT"),
        nullable=False,
    )

    # Product identity & SKU
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    # Financial price & currency (NUMERIC precision, NEVER float)
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Extensible non-sensitive metadata JSONB payload (ZERO secrets)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
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

    # ORM Relationship back to Merchant
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="products")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING metadata_payload."""
        return (
            f"<Product id={self.id} tenant_id={self.tenant_id} "
            f"merchant_id={self.merchant_id} sku='{self.sku}' status='{self.status}'>"
        )
