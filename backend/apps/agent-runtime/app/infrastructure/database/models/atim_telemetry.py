"""ATIMExecutionTelemetry ORM model for AGENTPAY (Phase 10 / Group 5)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Index, Integer, Numeric, PrimaryKeyConstraint, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ATIMExecutionTelemetry(Base):
    """ATIMExecutionTelemetry ORM entity representing execution logs & telemetry metrics."""

    __tablename__ = "atim_execution_telemetry"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_execution_telemetry"),
        Index("ix_atim_execution_telemetry_tenant_id", "tenant_id"),
        Index("ix_atim_execution_telemetry_agent_id", "agent_id"),
        Index("ix_atim_execution_telemetry_created_at", "created_at"),
        Index("ix_atim_execution_telemetry_tenant_created", "tenant_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    prompt_text: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    action: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, default="USD")

    is_security_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    security_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    security_reason: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    selected_model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    task_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    complexity: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    latency_ms: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    estimated_cost_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 6), nullable=True, default=Decimal("0.000000")
    )

    agentguard_decision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fraudguard_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    hitl_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    execution_decision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
