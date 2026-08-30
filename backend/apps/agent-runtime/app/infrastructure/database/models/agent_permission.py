"""AgentPermission ORM model module for AGENTPAY (Phase 035)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.permission import Permission


class AgentPermission(Base):
    """AgentPermission ORM entity representing direct permission assignments to an Agent."""

    __tablename__ = "agent_permissions"

    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "permission_id",
            name="uq_agent_permissions_agent_id_permission_id",
        ),
        Index("ix_agent_permissions_tenant_id", "tenant_id"),
        Index("ix_agent_permissions_agent_id", "agent_id"),
        Index("ix_agent_permissions_permission_id", "permission_id"),
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
        ForeignKey("agents.id", name="fk_agent_permissions_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Foreign key referencing permissions.id
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "permissions.id",
            name="fk_agent_permissions_permission_id_permissions",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    agent: Mapped["Agent"] = relationship("Agent")
    permission: Mapped["Permission"] = relationship("Permission")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<AgentPermission id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} permission_id={self.permission_id}>"
        )
