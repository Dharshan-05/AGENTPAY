"""AgentLifecycle ORM model module for AGENTPAY (Phase 037)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent


class AgentLifecycle(Base):
    """AgentLifecycle ORM entity representing current operational runtime state of an Agent."""

    __tablename__ = "agent_lifecycle"

    __table_args__ = (
        UniqueConstraint("agent_id", name="uq_agent_lifecycle_agent_id"),
        Index("ix_agent_lifecycle_tenant_id", "tenant_id"),
        Index("ix_agent_lifecycle_agent_id", "agent_id"),
        Index("ix_agent_lifecycle_status", "status"),
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

    # Foreign key referencing agents.id (1-to-1 relationship per agent)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", name="fk_agent_lifecycle_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Operational status and reason
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="provisioning",
    )
    status_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # State transition timestamps
    activated_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    suspended_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    last_transition_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Record timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ORM Relationship back to Agent
    agent: Mapped["Agent"] = relationship(
        "Agent",
        back_populates="lifecycle",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<AgentLifecycle id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} status='{self.status}'>"
        )
