"""agent_memories_table

Revision ID: 038_agent_memories
Revises: 037_user_preferences
Create Date: 2026-08-26 13:00:00.000000

Creates the agent_memories table for Phase 153 and Phase 154.
Stores agent short-term and unified memory records with isolation, TTL, and metadata.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "038_agent_memories"
down_revision: str | None = "037_user_preferences"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create agent_memories table."""
    op.create_table(
        "agent_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("memory_type", sa.String(length=50), nullable=False, server_default="short_term"),
        sa.Column("namespace", sa.String(length=100), nullable=False, server_default="default"),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column(
            "value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("importance", sa.Numeric(precision=5, scale=2), nullable=False, server_default="0.5"),  # noqa: E501
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=False, server_default="1.0"),  # noqa: E501
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_memories_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_memories"),
        sa.UniqueConstraint(
            "tenant_id",
            "agent_id",
            "namespace",
            "key",
            name="uq_agent_memories_tenant_agent_namespace_key",
        ),
    )
    op.create_index("ix_agent_memories_tenant_id", "agent_memories", ["tenant_id"], unique=False)
    op.create_index("ix_agent_memories_agent_id", "agent_memories", ["agent_id"], unique=False)
    op.create_index("ix_agent_memories_session_id", "agent_memories", ["session_id"], unique=False)
    op.create_index("ix_agent_memories_task_id", "agent_memories", ["task_id"], unique=False)
    op.create_index("ix_agent_memories_expires_at", "agent_memories", ["expires_at"], unique=False)


def downgrade() -> None:
    """Drop agent_memories table."""
    op.drop_index("ix_agent_memories_expires_at", table_name="agent_memories")
    op.drop_index("ix_agent_memories_task_id", table_name="agent_memories")
    op.drop_index("ix_agent_memories_session_id", table_name="agent_memories")
    op.drop_index("ix_agent_memories_agent_id", table_name="agent_memories")
    op.drop_index("ix_agent_memories_tenant_id", table_name="agent_memories")
    op.drop_table("agent_memories")
