"""AgentIdentity ORM model module for AGENTPAY (Phase 032)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent


class AgentIdentity(Base):
    """AgentIdentity ORM entity representing the identity profile of an Agent (zero credentials)."""

    __tablename__ = "agent_identities"

    __table_args__ = (
        UniqueConstraint("agent_id", name="uq_agent_identities_agent_id"),
        Index("ix_agent_identities_tenant_id", "tenant_id"),
        Index("ix_agent_identities_agent_id", "agent_id"),
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
        ForeignKey("agents.id", name="fk_agent_identities_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Non-secret identity attributes
    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    identity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="standard",
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    # ORM Relationship back to Agent
    agent: Mapped["Agent"] = relationship(
        "Agent",
        back_populates="identity",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<AgentIdentity id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} identity_type='{self.identity_type}'>"
        )
