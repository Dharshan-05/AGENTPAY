"""Merchant ORM model module for AGENTPAY (Phase 041)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.product import Product


class Merchant(Base):
    """Merchant ORM entity representing a commercial business entity in AGENTPAY."""

    __tablename__ = "merchants"

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_merchants_tenant_id_slug"),
        Index("ix_merchants_tenant_id", "tenant_id"),
        Index("ix_merchants_status", "status"),
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

    # Merchant identity
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
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

    # ORM Relationship to Products
    products: Mapped[list["Product"]] = relationship("Product", back_populates="merchant")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<Merchant id={self.id} tenant_id={self.tenant_id} "
            f"slug='{self.slug}' status='{self.status}'>"
        )
