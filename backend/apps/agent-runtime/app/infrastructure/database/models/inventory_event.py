"""InventoryEvent ORM model module for AGENTPAY (Phase 045)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.inventory import Inventory
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.product import Product


class InventoryEvent(Base):
    """InventoryEvent ORM entity representing append-only inventory events in AGENTPAY."""

    __tablename__ = "inventory_events"

    __table_args__ = (
        CheckConstraint(
            "quantity_after = quantity_before + quantity_delta",
            name="quantity_after_consistency",
        ),
        CheckConstraint("quantity_before >= 0", name="quantity_before_nonnegative"),
        CheckConstraint("quantity_after >= 0", name="quantity_after_nonnegative"),
        Index("ix_inventory_events_tenant_id", "tenant_id"),
        Index("ix_inventory_events_inventory_id", "inventory_id"),
        Index("ix_inventory_events_merchant_id", "merchant_id"),
        Index("ix_inventory_events_product_id", "product_id"),
        Index("ix_inventory_events_event_type", "event_type"),
        Index("ix_inventory_events_occurred_at", "occurred_at"),
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
    inventory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "inventory.id",
            name="fk_inventory_events_inventory_id_inventory",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_inventory_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_inventory_events_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Event classification & status
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
    )

    # Quantity changes (NUMERIC precision 18,3 - NEVER float)
    quantity_delta: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )
    quantity_before: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )
    quantity_after: Mapped[Decimal] = mapped_column(
        Numeric(18, 3),
        nullable=False,
        default=Decimal("0.000"),
    )

    reserved_quantity_delta: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 3),
        nullable=True,
    )
    reserved_quantity_before: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 3),
        nullable=True,
    )
    reserved_quantity_after: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 3),
        nullable=True,
    )

    # Operational context
    reference_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
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
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Timestamps (Append-only: NO updated_at, NO deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory")
    merchant: Mapped["Merchant"] = relationship("Merchant")
    product: Mapped["Product"] = relationship("Product")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<InventoryEvent id={self.id} tenant_id={self.tenant_id} "
            f"inventory_id={self.inventory_id} event_type='{self.event_type}' "
            f"event_action='{self.event_action}' result='{self.event_result}'>"
        )
