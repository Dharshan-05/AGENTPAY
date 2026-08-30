"""AgentSession ORM model module for AGENTPAY (Phase 034)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.agent_credential import AgentCredential


class AgentSession(Base):
    """AgentSession ORM entity representing an active/historical Agent runtime session context."""

    __tablename__ = "agent_sessions"

    __table_args__ = (
        Index("ix_agent_sessions_tenant_id", "tenant_id"),
        Index("ix_agent_sessions_agent_id", "agent_id"),
        Index("ix_agent_sessions_credential_id", "credential_id"),
        Index("ix_agent_sessions_status", "status"),
        Index("ix_agent_sessions_expires_at", "expires_at"),
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

    # Foreign key referencing agents.id
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", name="fk_agent_sessions_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Foreign key referencing agent_credentials.id (optional)
    credential_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agent_credentials.id",
            name="fk_agent_sessions_credential_id_agent_credentials",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Status & context metadata
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    device_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Session metadata (controlled JSONB payload with ZERO secrets)
    session_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    # Activity & expiration boundaries
    last_activity_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    revocation_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ORM Relationships
    agent: Mapped["Agent"] = relationship(
        "Agent",
        back_populates="sessions",
    )
    credential: Mapped[Optional["AgentCredential"]] = relationship("AgentCredential")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING sensitive metadata."""
        return (
            f"<AgentSession id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} status='{self.status}'>"
        )
