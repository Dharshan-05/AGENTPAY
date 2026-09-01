"""PaymentEvent ORM model module for AGENTPAY (Phase 063)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.payment_order import PaymentOrder
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction


class PaymentEvent(Base):
    """PaymentEvent ORM entity representing append-only payment processing events in AGENTPAY."""

    __tablename__ = "payment_events"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_payment_events_tenant_id_event_reference",
        ),
        UniqueConstraint(
            "payment_transaction_id",
            "sequence_number",
            name="uq_payment_events_transaction_sequence",
        ),
        CheckConstraint(
            "event_type IN ('payment', 'authorization', 'capture', "
            "'failure', 'cancellation', 'lifecycle')",
            name="event_type",
        ),
        CheckConstraint(
            "event_action IN ('created', 'requested', 'processing', "
            "'authorized', 'completed', 'failed', 'cancelled')",
            name="event_action",
        ),
        CheckConstraint(
            "event_result IN ('success', 'failure', 'pending')",
            name="event_result",
        ),
        CheckConstraint(
            "sequence_number > 0",
            name="sequence_number_positive",
        ),
        Index("ix_payment_events_tenant_id", "tenant_id"),
        Index("ix_payment_events_payment_transaction_id", "payment_transaction_id"),
        Index("ix_payment_events_payment_order_id", "payment_order_id"),
        Index("ix_payment_events_event_type", "event_type"),
        Index("ix_payment_events_event_action", "event_action"),
        Index("ix_payment_events_event_result", "event_result"),
        Index("ix_payment_events_request_id", "request_id"),
        Index("ix_payment_events_occurred_at", "occurred_at"),
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

    # Required Relationship to PaymentTransaction
    payment_transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_payment_events_ptxn_id_ptxns",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Optional Foreign Key to PaymentOrder
    payment_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_orders.id",
            name="fk_payment_events_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Classification
    event_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    event_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    event_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Deterministic Sequence Ordering
    sequence_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Correlation Context
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

    # Non-secret JSONB Metadata
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Immutable Append-Only Timestamps (STRICTLY NO updated_at or deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    payment_transaction: Mapped["PaymentTransaction"] = relationship(
        "PaymentTransaction",
        back_populates="payment_events",
    )
    payment_order: Mapped[Optional["PaymentOrder"]] = relationship(
        "PaymentOrder",
        back_populates="payment_events",
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding JSONB metadata."""
        return (
            f"<PaymentEvent id={self.id} tenant_id={self.tenant_id} "
            f"transaction_id={self.payment_transaction_id} seq={self.sequence_number} "
            f"type='{self.event_type}' action='{self.event_action}' result='{self.event_result}'>"
        )
