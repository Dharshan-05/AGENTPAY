"""atim_execution_telemetry_table

Revision ID: 041_atim_execution_telemetry
Revises: 040_tool_execution_audit
Create Date: 2026-08-31 18:00:00.000000

Creates the atim_execution_telemetry table for Phase 10 / Group 5.
Stores execution logs, model routing telemetry, cost metrics, and security audits for ATIM.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "041_atim_execution_telemetry"
down_revision: str | None = "040_tool_execution_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create atim_execution_telemetry table."""
    op.create_table(
        "atim_execution_telemetry",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("prompt_text", sa.String(length=2048), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=True),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True, server_default="USD"),
        sa.Column("is_security_blocked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("security_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("security_reason", sa.String(length=256), nullable=True),
        sa.Column("selected_model", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("task_type", sa.String(length=64), nullable=True),
        sa.Column("complexity", sa.String(length=32), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=True),
        sa.Column("latency_ms", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=12, scale=6), nullable=True, server_default="0.000000"),
        sa.Column("agentguard_decision", sa.String(length=64), nullable=True),
        sa.Column("fraudguard_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("hitl_required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("execution_decision", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_atim_execution_telemetry"),
    )

    op.create_index("ix_atim_execution_telemetry_tenant_id", "atim_execution_telemetry", ["tenant_id"])
    op.create_index("ix_atim_execution_telemetry_agent_id", "atim_execution_telemetry", ["agent_id"])
    op.create_index("ix_atim_execution_telemetry_created_at", "atim_execution_telemetry", ["created_at"])
    op.create_index("ix_atim_execution_telemetry_tenant_created", "atim_execution_telemetry", ["tenant_id", "created_at"])


def downgrade() -> None:
    """Drop atim_execution_telemetry table."""
    op.drop_index("ix_atim_execution_telemetry_tenant_created", table_name="atim_execution_telemetry")
    op.drop_index("ix_atim_execution_telemetry_created_at", table_name="atim_execution_telemetry")
    op.drop_index("ix_atim_execution_telemetry_agent_id", table_name="atim_execution_telemetry")
    op.drop_index("ix_atim_execution_telemetry_tenant_id", table_name="atim_execution_telemetry")
    op.drop_table("atim_execution_telemetry")
