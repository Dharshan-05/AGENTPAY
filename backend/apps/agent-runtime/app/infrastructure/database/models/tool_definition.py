"""Tool Definition ORM model module for AGENTPAY (Phase 157)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ToolDefinition(Base):
    """ORM entity representing registered agent tools in AGENTPAY (Phase 157)."""

    __tablename__ = "tool_definitions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "name",
            "version",
            name="uq_tool_definitions_tenant_name_version",
        ),
        Index("ix_tool_definitions_tenant_id", "tenant_id"),
        Index("ix_tool_definitions_tool_id", "tool_id"),
        Index("ix_tool_definitions_name", "name"),
        Index("ix_tool_definitions_category", "category"),
        Index("ix_tool_definitions_status", "status"),
        Index("ix_tool_definitions_risk_classification", "risk_classification"),
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

    # Tool Metadata & Identification
    tool_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="utility",
    )
    owner: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="REGISTERED",
    )
    environment: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="production",
    )
    risk_classification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="LOW",
    )

    # Tool Schemas & Capability Metadata
    input_schema: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    output_schema: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    capabilities: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    tool_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Timestamps & Soft Delete
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
