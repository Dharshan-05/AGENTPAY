"""AgentRole ORM model module for AGENTPAY (Phase 036)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.role import Role


class AgentRole(Base):
    """AgentRole ORM entity representing role assignments to autonomous Agents."""

    __tablename__ = "agent_roles"

    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "role_id",
            name="uq_agent_roles_agent_id_role_id",
        ),
        Index("ix_agent_roles_tenant_id", "tenant_id"),
        Index("ix_agent_roles_agent_id", "agent_id"),
        Index("ix_agent_roles_role_id", "role_id"),
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
        ForeignKey("agents.id", name="fk_agent_roles_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Foreign key referencing roles.id
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", name="fk_agent_roles_role_id_roles", ondelete="RESTRICT"),
        nullable=False,
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    agent: Mapped["Agent"] = relationship("Agent")
    role: Mapped["Role"] = relationship("Role")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<AgentRole id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} role_id={self.role_id}>"
        )
