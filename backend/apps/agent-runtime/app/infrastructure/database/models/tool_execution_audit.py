"""Tool Execution Audit ORM model module for AGENTPAY (Phase 159)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ToolExecutionAudit(Base):
    """ORM entity representing immutable audit records for tool executions (Phase 159)."""

    __tablename__ = "tool_execution_audits"

    __table_args__ = (
        Index("ix_tool_exec_audits_tenant_id", "tenant_id"),
        Index("ix_tool_exec_audits_agent_id", "agent_id"),
        Index("ix_tool_exec_audits_user_id", "user_id"),
        Index("ix_tool_exec_audits_tool_id", "tool_id"),
        Index("ix_tool_exec_audits_execution_id", "execution_id"),
        Index("ix_tool_exec_audits_correlation_id", "correlation_id"),
        Index("ix_tool_exec_audits_execution_state", "execution_state"),
        Index("ix_tool_exec_audits_created_at", "created_at"),
    )

    # Primary key (UUIDv7)
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

    # Execution Telemetry Identifiers
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Tool Metadata
    tool_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    tool_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
    )

    # Security & Execution Decisions
    permission_decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ALLOW",
    )
    approval_state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="NOT_REQUIRED",
    )
    execution_state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    risk_classification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="LOW",
    )

    # Telemetry Timings
    duration_ms: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0.0,
    )
    error_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    environment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="production",
    )

    # Payload Metadata (Sanitized & Redacted)
    payload_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Creation Timestamp (Append-Only Immutable)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
