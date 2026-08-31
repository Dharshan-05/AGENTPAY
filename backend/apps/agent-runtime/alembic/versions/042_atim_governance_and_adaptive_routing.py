"""atim_governance_and_adaptive_routing_tables

Revision ID: 042_atim_governance_and_adaptive_routing
Revises: 041_atim_execution_telemetry
Create Date: 2026-08-31 18:30:00.000000

Creates atim_model_versions, atim_governance_decisions, atim_cost_budgets, and atim_task_performance_stats tables for Group 6 (Phases 11 & 12).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "042_atim_governance_and_adaptive_routing"
down_revision: str | None = "041_atim_execution_telemetry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create Group 6 governance & adaptive routing tables."""
    # 1. atim_model_versions
    op.create_table(
        "atim_model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("provider_name", sa.String(length=64), nullable=False),
        sa.Column("version_tag", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="CANDIDATE"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_atim_model_versions"),
    )
    op.create_index("ix_atim_model_versions_model_id", "atim_model_versions", ["model_id"])
    op.create_index("ix_atim_model_versions_status", "atim_model_versions", ["status"])

    # 2. atim_governance_decisions
    op.create_table(
        "atim_governance_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_type", sa.String(length=32), nullable=False, server_default="SYSTEM"),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False, server_default="v1.0.0"),
        sa.Column("dataset_version", sa.String(length=64), nullable=False, server_default="v1.0.0"),
        sa.Column("previous_status", sa.String(length=32), nullable=False),
        sa.Column("new_status", sa.String(length=32), nullable=False),
        sa.Column("decision_reason", sa.String(length=512), nullable=False),
        sa.Column("security_score", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.9500"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_atim_governance_decisions"),
    )
    op.create_index("ix_atim_governance_decisions_tenant_id", "atim_governance_decisions", ["tenant_id"])
    op.create_index("ix_atim_governance_decisions_model_id", "atim_governance_decisions", ["model_id"])
    op.create_index("ix_atim_governance_decisions_created_at", "atim_governance_decisions", ["created_at"])

    # 3. atim_cost_budgets
    op.create_table(
        "atim_cost_budgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("max_cost_per_request", sa.Numeric(precision=12, scale=6), nullable=False, server_default="0.050000"),
        sa.Column("daily_budget_usd", sa.Numeric(precision=12, scale=6), nullable=False, server_default="50.000000"),
        sa.Column("monthly_budget_usd", sa.Numeric(precision=12, scale=6), nullable=False, server_default="1000.000000"),
        sa.Column("current_daily_spend_usd", sa.Numeric(precision=12, scale=6), nullable=False, server_default="0.000000"),
        sa.Column("current_monthly_spend_usd", sa.Numeric(precision=12, scale=6), nullable=False, server_default="0.000000"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_atim_cost_budgets"),
    )
    op.create_index("ix_atim_cost_budgets_tenant_id", "atim_cost_budgets", ["tenant_id"])
    op.create_index("ix_atim_cost_budgets_agent_id", "atim_cost_budgets", ["agent_id"])
    op.create_index("ix_atim_cost_budgets_tenant_agent", "atim_cost_budgets", ["tenant_id", "agent_id"])

    # 4. atim_task_performance_stats
    op.create_table(
        "atim_task_performance_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", sa.String(length=128), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=4), nullable=False, server_default="1.0000"),
        sa.Column("avg_latency_ms", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0.00"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_atim_task_performance_stats"),
    )
    op.create_index("ix_atim_task_performance_stats_model_task", "atim_task_performance_stats", ["model_id", "task_type"])


def downgrade() -> None:
    """Drop Group 6 governance & adaptive routing tables."""
    op.drop_index("ix_atim_task_performance_stats_model_task", table_name="atim_task_performance_stats")
    op.drop_table("atim_task_performance_stats")

    op.drop_index("ix_atim_cost_budgets_tenant_agent", table_name="atim_cost_budgets")
    op.drop_index("ix_atim_cost_budgets_agent_id", table_name="atim_cost_budgets")
    op.drop_index("ix_atim_cost_budgets_tenant_id", table_name="atim_cost_budgets")
    op.drop_table("atim_cost_budgets")

    op.drop_index("ix_atim_governance_decisions_created_at", table_name="atim_governance_decisions")
    op.drop_index("ix_atim_governance_decisions_model_id", table_name="atim_governance_decisions")
    op.drop_index("ix_atim_governance_decisions_tenant_id", table_name="atim_governance_decisions")
    op.drop_table("atim_governance_decisions")

    op.drop_index("ix_atim_model_versions_status", table_name="atim_model_versions")
    op.drop_index("ix_atim_model_versions_model_id", table_name="atim_model_versions")
    op.drop_table("atim_model_versions")
