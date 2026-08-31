"""ATIM Phase 24 Multi-Agent Distributed Consensus ORM Entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.atim_workflow import ATIMWorkflowInstance
    from app.infrastructure.database.models.user import Tenant


class ATIMConsensusSession(Base):
    """SQLAlchemy 2.x entity representing a multi-agent consensus session (Group 13 / Phase 24)."""

    __tablename__ = "atim_consensus_sessions"
    __table_args__ = (
        Index("ix_atim_consensus_sessions_tenant_id", "tenant_id"),
        Index("ix_atim_consensus_sessions_proposer_agent_id", "proposer_agent_id"),
        Index("ix_atim_consensus_sessions_workflow_id", "workflow_id"),
        Index("ix_atim_consensus_sessions_status", "status"),
        {"comment": "ATIM Phase 24 Multi-Agent Distributed Consensus Sessions"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    proposer_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    workflow_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("atim_workflow_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    required_quorum: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="INITIATED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    votes: Mapped[List[ATIMConsensusVote]] = relationship(
        "ATIMConsensusVote",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ATIMConsensusVote(Base):
    """SQLAlchemy 2.x entity representing an individual agent's vote in a consensus session."""

    __tablename__ = "atim_consensus_votes"
    __table_args__ = (
        UniqueConstraint("session_id", "voter_agent_id", name="uq_session_voter"),
        Index("ix_atim_consensus_votes_session_id", "session_id"),
        Index("ix_atim_consensus_votes_tenant_id", "tenant_id"),
        Index("ix_atim_consensus_votes_voter_agent_id", "voter_agent_id"),
        {"comment": "ATIM Phase 24 Multi-Agent Consensus Individual Votes"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("atim_consensus_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    voter_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    vote: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    vote_signature: Mapped[str] = mapped_column(String(256), nullable=False)
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    session: Mapped[ATIMConsensusSession] = relationship(
        "ATIMConsensusSession",
        back_populates="votes",
    )
