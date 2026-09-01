"""ProductCategory ORM model module for AGENTPAY (Phase 043)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.merchant import Merchant


class ProductCategory(Base):
    """ProductCategory ORM entity representing product categorization hierarchy in AGENTPAY."""

    __tablename__ = "product_categories"

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_product_categories_tenant_id_slug"),
        CheckConstraint(
            "parent_category_id IS NULL OR parent_category_id <> id",
            name="parent_not_self",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'archived')",
            name="status",
        ),
        Index("ix_product_categories_tenant_id", "tenant_id"),
        Index("ix_product_categories_merchant_id", "merchant_id"),
        Index("ix_product_categories_parent_category_id", "parent_category_id"),
        Index("ix_product_categories_status", "status"),
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
        ForeignKey(
            "merchants.id",
            name="fk_product_categories_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Category identity & slug
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

    # Hierarchy: Self-referencing parent category
    parent_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "product_categories.id",
            name="fk_short_74121343",
            ondelete="RESTRICT",
        ),
        nullable=True,
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
    parent_category: Mapped[Optional["ProductCategory"]] = relationship(
        "ProductCategory",
        remote_side=[id],
        back_populates="subcategories",
    )
    subcategories: Mapped[list["ProductCategory"]] = relationship(
        "ProductCategory",
        back_populates="parent_category",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<ProductCategory id={self.id} tenant_id={self.tenant_id} "
            f"merchant_id={self.merchant_id} slug='{self.slug}' status='{self.status}'>"
        )
