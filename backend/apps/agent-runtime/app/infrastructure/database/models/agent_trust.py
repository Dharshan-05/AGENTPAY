"""AgentTrust ORM model module for AGENTPAY (Phase 039)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent


class AgentTrust(Base):
    """AgentTrust ORM entity representing current security posture of an Agent."""

    __tablename__ = "agent_trust"

    __table_args__ = (
        UniqueConstraint("agent_id", name="uq_agent_trust_agent_id"),
        CheckConstraint(
            "trust_score IS NULL OR (trust_score >= 0 AND trust_score <= 100)",
            name="score_range",
        ),
        Index("ix_agent_trust_tenant_id", "tenant_id"),
        Index("ix_agent_trust_agent_id", "agent_id"),
        Index("ix_agent_trust_trust_status", "trust_status"),
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
        ForeignKey("agents.id", name="fk_agent_trust_agent_id_agents", ondelete="RESTRICT"),
        nullable=False,
    )

    # Trust status and numerical score
    trust_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unknown",
    )
    trust_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    trust_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Extensible non-sensitive trust posture metadata JSONB payload (ZERO secrets)
    trust_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    # Timestamps
    evaluated_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
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
        """Return safe string representation REDACTING trust_metadata."""
        return (
            f"<AgentTrust id={self.id} tenant_id={self.tenant_id} "
            f"agent_id={self.agent_id} trust_status='{self.trust_status}'>"
        )
