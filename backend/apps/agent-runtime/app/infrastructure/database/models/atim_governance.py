"""SQLAlchemy ORM models for ATIM Model Governance & Adaptive Routing (Phases 11 & 12)."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from sqlalchemy import Boolean, Index, Integer, Numeric, PrimaryKeyConstraint, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ATIMModelVersion(Base):
    """ORM table for immutable model version registrations."""

    __tablename__ = "atim_model_versions"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_model_versions"),
        Index("ix_atim_model_versions_model_id", "model_id"),
        Index("ix_atim_model_versions_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False)
    version_tag: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="CANDIDATE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


class ATIMGovernanceDecision(Base):
    """ORM table for immutable governance audit decisions."""

    __tablename__ = "atim_governance_decisions"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_governance_decisions"),
        Index("ix_atim_governance_decisions_tenant_id", "tenant_id"),
        Index("ix_atim_governance_decisions_model_id", "model_id"),
        Index("ix_atim_governance_decisions_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(32), default="SYSTEM", nullable=False)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), default="v1.0.0", nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(64), default="v1.0.0", nullable=False)
    previous_status: Mapped[str] = mapped_column(String(32), nullable=False)
    new_status: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_reason: Mapped[str] = mapped_column(String(512), nullable=False)
    security_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.9500"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


class ATIMCostBudget(Base):
    """ORM table for tenant and agent cost budget quotas."""

    __tablename__ = "atim_cost_budgets"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_cost_budgets"),
        Index("ix_atim_cost_budgets_tenant_id", "tenant_id"),
        Index("ix_atim_cost_budgets_agent_id", "agent_id"),
        Index("ix_atim_cost_budgets_tenant_agent", "tenant_id", "agent_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    max_cost_per_request: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("0.050000"), nullable=False)
    daily_budget_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("50.000000"), nullable=False)
    monthly_budget_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("1000.000000"), nullable=False)
    current_daily_spend_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("0.000000"), nullable=False)
    current_monthly_spend_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("0.000000"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())


class ATIMTaskPerformanceStats(Base):
    """ORM table for task-specific model performance metrics."""

    __tablename__ = "atim_task_performance_stats"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_atim_task_performance_stats"),
        Index("ix_atim_task_performance_stats_model_task", "model_id", "task_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quality_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("1.0000"), nullable=False)
    avg_latency_ms: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())
