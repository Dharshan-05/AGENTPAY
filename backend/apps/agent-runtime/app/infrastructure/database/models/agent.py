"""Agent ORM model module for AGENTPAY (Phase 031)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent_credential import AgentCredential
    from app.infrastructure.database.models.agent_identity import AgentIdentity
    from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle
    from app.infrastructure.database.models.agent_session import AgentSession


class Agent(Base):
    """Agent ORM entity representing a first-class autonomous agent principal."""

    __tablename__ = "agents"

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_agents_tenant_id_slug"),
        Index("ix_agents_tenant_id", "tenant_id"),
        Index("ix_agents_slug", "slug"),
        Index("ix_agents_status", "status"),
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

    # Core agent identity fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    agent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="autonomous",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps & Soft delete
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

    # Relationship to AgentIdentity (1-to-1)
    identity: Mapped[Optional["AgentIdentity"]] = relationship(
        "AgentIdentity",
        back_populates="agent",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Relationship to AgentCredential (1-to-many)
    credentials: Mapped[list["AgentCredential"]] = relationship(
        "AgentCredential",
        back_populates="agent",
        cascade="all, delete-orphan",
    )

    # Relationship to AgentLifecycle (1-to-1)
    lifecycle: Mapped[Optional["AgentLifecycle"]] = relationship(
        "AgentLifecycle",
        back_populates="agent",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Relationship to AgentSession (1-to-many)
    sessions: Mapped[list["AgentSession"]] = relationship(
        "AgentSession",
        back_populates="agent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<Agent id={self.id} tenant_id={self.tenant_id} "
            f"name='{self.name}' slug='{self.slug}' status='{self.status}'>"
        )
