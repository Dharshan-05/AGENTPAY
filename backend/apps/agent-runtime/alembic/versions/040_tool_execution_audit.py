"""tool_execution_audit_table

Revision ID: 040_tool_execution_audit
Revises: 039_tool_registry
Create Date: 2026-08-26 15:00:00.000000

Creates the tool_execution_audits table for Phase 159.
Stores immutable append-only telemetry logs for all tool execution attempts.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "040_tool_execution_audit"
down_revision: str | None = "039_tool_registry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tool_execution_audits table."""
    op.create_table(
        "tool_execution_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
        sa.Column("tool_id", sa.String(length=100), nullable=False),
        sa.Column("tool_version", sa.String(length=20), nullable=False, server_default="1.0.0"),
        sa.Column("permission_decision", sa.String(length=50), nullable=False, server_default="ALLOW"),  # noqa: E501
        sa.Column("approval_state", sa.String(length=50), nullable=False, server_default="NOT_REQUIRED"),  # noqa: E501
        sa.Column("execution_state", sa.String(length=50), nullable=False),
        sa.Column("risk_classification", sa.String(length=50), nullable=False, server_default="LOW"),  # noqa: E501
        sa.Column("duration_ms", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0.0"),  # noqa: E501
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("environment", sa.String(length=50), nullable=False, server_default="production"),
        sa.Column(
            "payload_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_tool_exec_audits_tenant_id", "tool_execution_audits", ["tenant_id"])
    op.create_index("ix_tool_exec_audits_agent_id", "tool_execution_audits", ["agent_id"])
    op.create_index("ix_tool_exec_audits_user_id", "tool_execution_audits", ["user_id"])
    op.create_index("ix_tool_exec_audits_tool_id", "tool_execution_audits", ["tool_id"])
    op.create_index("ix_tool_exec_audits_execution_id", "tool_execution_audits", ["execution_id"])
    op.create_index("ix_tool_exec_audits_correlation_id", "tool_execution_audits", ["correlation_id"])  # noqa: E501
    op.create_index("ix_tool_exec_audits_execution_state", "tool_execution_audits", ["execution_state"])  # noqa: E501
    op.create_index("ix_tool_exec_audits_created_at", "tool_execution_audits", ["created_at"])


def downgrade() -> None:
    """Drop tool_execution_audits table."""
    op.drop_index("ix_tool_exec_audits_created_at", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_execution_state", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_correlation_id", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_execution_id", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_tool_id", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_user_id", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_agent_id", table_name="tool_execution_audits")
    op.drop_index("ix_tool_exec_audits_tenant_id", table_name="tool_execution_audits")
    op.drop_table("tool_execution_audits")
