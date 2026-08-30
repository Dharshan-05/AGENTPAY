"""Agent Memory ORM model module for AGENTPAY (Phase 153 & Phase 154)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class AgentMemory(Base):
    """ORM model representing agent short-term and unified memory records (Phase 153/154)."""

    __tablename__ = "agent_memories"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "agent_id",
            "namespace",
            "key",
            name="uq_agent_memories_tenant_agent_namespace_key",
        ),
        Index("ix_agent_memories_tenant_id", "tenant_id"),
        Index("ix_agent_memories_agent_id", "agent_id"),
        Index("ix_agent_memories_session_id", "session_id"),
        Index("ix_agent_memories_task_id", "task_id"),
        Index("ix_agent_memories_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="short_term",
    )
    namespace: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="default",
    )
    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    value: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    importance: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0.5,
    )
    confidence: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=1.0,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
