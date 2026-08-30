"""AgentCredential ORM model module for AGENTPAY (Phase 033)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent


class AgentCredential(Base):
    """AgentCredential ORM entity representing one-way hashed verification records for Agents."""

    __tablename__ = "agent_credentials"

    __table_args__ = (
        Index("ix_agent_credentials_tenant_id", "tenant_id"),
        Index("ix_agent_credentials_agent_id", "agent_id"),
        Index("ix_agent_credentials_credential_identifier", "credential_identifier"),
        Index("ix_agent_credentials_status", "status"),
        Index("ix_agent_credentials_expires_at", "expires_at"),
        Index("ix_agent_credentials_replaced_by_credential_id", "replaced_by_credential_id"),
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
        ForeignKey("agents.id", name="fk_agent_credentials_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Non-secret lookup identifier and type
    credential_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    credential_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # One-way cryptographic secret verification hash (NEVER raw secret)
    secret_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Status & boundaries
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Rotation reference
    replaced_by_credential_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agent_credentials.id",
            name="fk_agent_credentials_replaced_by_credential_id_agent_credentials",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Timestamps
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
        back_populates="credentials",
    )

    def __repr__(self) -> str:
        """Return safe string representation REDACTING secret_hash."""
        return (
            f"<AgentCredential id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} type='{self.credential_type}' "
            f"status='{self.status}'>"
        )
