"""AgentAudit ORM model module for AGENTPAY (Phase 040)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent


class AgentAudit(Base):
    """AgentAudit ORM entity representing immutable append-only audit trail for Agent operations."""

    __tablename__ = "agent_audit"

    __table_args__ = (
        Index("ix_agent_audit_tenant_id", "tenant_id"),
        Index("ix_agent_audit_agent_id", "agent_id"),
        Index("ix_agent_audit_actor_type", "actor_type"),
        Index("ix_agent_audit_actor_id", "actor_id"),
        Index("ix_agent_audit_event_type", "event_type"),
        Index("ix_agent_audit_occurred_at", "occurred_at"),
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

    # Foreign key referencing agents.id (1-to-many audit events per agent)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", name="fk_agent_audit_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Actor information
    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Event classification and result
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

    # Request context
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Extensible structured non-secret event metadata payload (ZERO secrets)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    # Occurrence & creation timestamp (Append-only by design: NO updated_at, NO deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationship back to Agent
    agent: Mapped["Agent"] = relationship("Agent")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING event_metadata."""
        return (
            f"<AgentAudit id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} event_type='{self.event_type}'>"
        )
