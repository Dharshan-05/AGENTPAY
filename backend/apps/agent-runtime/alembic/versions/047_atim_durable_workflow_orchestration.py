"""Alembic migration 047: ATIM Durable Workflow Instances & Step Executions (Phase 23 / Group 12)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "047"
down_revision: Union[str, None] = "046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: atim_workflow_instances
    op.create_table(
        "atim_workflow_instances",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("workflow_type", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="INITIATED"),
        sa.Column("current_step_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_steps", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signature", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_atim_workflow_instances"),
    )
    op.create_index(
        "ix_atim_workflow_inst_tenant_state",
        "atim_workflow_instances",
        ["tenant_id", "state"],
    )
    op.create_index(
        "ix_atim_workflow_inst_created_at",
        "atim_workflow_instances",
        ["created_at"],
    )

    # 2. Table: atim_workflow_step_executions
    op.create_table(
        "atim_workflow_step_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("step_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="COMPLETED"),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("input_params", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_atim_workflow_step_executions"),
    )
    op.create_index(
        "ix_atim_workflow_step_unique",
        "atim_workflow_step_executions",
        ["workflow_id", "step_index"],
        unique=True,
    )
    op.create_index(
        "ix_atim_workflow_step_created_at",
        "atim_workflow_step_executions",
        ["started_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_atim_workflow_step_created_at", table_name="atim_workflow_step_executions")
    op.drop_index("ix_atim_workflow_step_unique", table_name="atim_workflow_step_executions")
    op.drop_table("atim_workflow_step_executions")

    op.drop_index("ix_atim_workflow_inst_created_at", table_name="atim_workflow_instances")
    op.drop_index("ix_atim_workflow_inst_tenant_state", table_name="atim_workflow_instances")
    op.drop_table("atim_workflow_instances")
