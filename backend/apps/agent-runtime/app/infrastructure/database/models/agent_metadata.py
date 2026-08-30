"""AgentMetadata ORM model module for AGENTPAY (Phase 038)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent


class AgentMetadata(Base):
    """AgentMetadata ORM entity representing metadata profile of an Agent."""

    __tablename__ = "agent_metadata"

    __table_args__ = (
        UniqueConstraint("agent_id", name="uq_agent_metadata_agent_id"),
        Index("ix_agent_metadata_tenant_id", "tenant_id"),
        Index("ix_agent_metadata_agent_id", "agent_id"),
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
        ForeignKey("agents.id", name="fk_agent_metadata_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Extensible non-sensitive metadata JSONB payload (ZERO secrets)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
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
    agent: Mapped["Agent"] = relationship("Agent")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING metadata_payload."""
        return f"<AgentMetadata id={self.id} tenant_id={self.tenant_id} agent_id={self.agent_id}>"
