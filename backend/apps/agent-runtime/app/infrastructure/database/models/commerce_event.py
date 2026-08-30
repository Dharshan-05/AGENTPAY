"""CommerceEvent ORM model module for AGENTPAY (Phase 050)."""

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
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
    from app.infrastructure.database.models.merchant import Merchant


class CommerceEvent(Base):
    """CommerceEvent ORM entity representing an immutable commerce event in AGENTPAY."""

    __tablename__ = "commerce_events"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_commerce_events_tenant_id_event_reference",
        ),
        UniqueConstraint(
            "transaction_id",
            "sequence_number",
            name="uq_commerce_events_transaction_id_sequence_number",
        ),
        CheckConstraint(
            "event_type IN ('transaction', 'authorization', 'capture', "
            "'refund', 'adjustment', 'lifecycle')",
            name="event_type",
        ),
        CheckConstraint(
            "event_action IN ('created', 'requested', 'approved', 'completed', "
            "'failed', 'cancelled', 'refunded')",
            name="event_action",
        ),
        CheckConstraint(
            "event_result IS NULL OR event_result IN ('success', 'failure', 'pending')",
            name="event_result",
        ),
        Index("ix_commerce_events_tenant_id", "tenant_id"),
        Index("ix_commerce_events_transaction_id", "transaction_id"),
        Index("ix_commerce_events_merchant_id", "merchant_id"),
        Index("ix_commerce_events_agent_id", "agent_id"),
        Index("ix_commerce_events_event_type", "event_type"),
        Index("ix_commerce_events_occurred_at", "occurred_at"),
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
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_commerce_events_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_commerce_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_commerce_events_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity & Reference
    event_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Event Classification
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_result: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Deterministic Sequence Number
    sequence_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Request / Actor Context
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

    # Event Metadata Payload (JSONB, zero secrets)
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
    transaction: Mapped["CommerceTransaction"] = relationship(
        "CommerceTransaction",
        back_populates="commerce_events",
    )
    merchant: Mapped["Merchant"] = relationship("Merchant")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<CommerceEvent id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.event_reference}' type='{self.event_type}' "
            f"action='{self.event_action}'>"
        )
