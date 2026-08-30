"""agent_lifecycle_and_metadata

Revision ID: 009_agent_lifecycle_and_metadata
Revises: 008_agent_permissions_and_roles
Create Date: 2026-08-25 22:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009_agent_lifecycle_and_metadata"
down_revision: str | None = "008_agent_permissions_and_roles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create agent_lifecycle table
    op.create_table(
        "agent_lifecycle",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="provisioning"),
        sa.Column("status_reason", sa.String(length=255), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_transition_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_lifecycle_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_lifecycle"),
        sa.UniqueConstraint("agent_id", name="uq_agent_lifecycle_agent_id"),
    )
    op.create_index("ix_agent_lifecycle_tenant_id", "agent_lifecycle", ["tenant_id"], unique=False)
    op.create_index("ix_agent_lifecycle_agent_id", "agent_lifecycle", ["agent_id"], unique=False)
    op.create_index("ix_agent_lifecycle_status", "agent_lifecycle", ["status"], unique=False)

    # 2. Create agent_metadata table
    op.create_table(
        "agent_metadata",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "metadata_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
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
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_metadata_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_metadata"),
        sa.UniqueConstraint("agent_id", name="uq_agent_metadata_agent_id"),
    )
    op.create_index("ix_agent_metadata_tenant_id", "agent_metadata", ["tenant_id"], unique=False)
    op.create_index("ix_agent_metadata_agent_id", "agent_metadata", ["agent_id"], unique=False)


def downgrade() -> None:
    # 1. Drop agent_metadata table
    op.drop_index("ix_agent_metadata_agent_id", table_name="agent_metadata")
    op.drop_index("ix_agent_metadata_tenant_id", table_name="agent_metadata")
    op.drop_table("agent_metadata")

    # 2. Drop agent_lifecycle table
    op.drop_index("ix_agent_lifecycle_status", table_name="agent_lifecycle")
    op.drop_index("ix_agent_lifecycle_agent_id", table_name="agent_lifecycle")
    op.drop_index("ix_agent_lifecycle_tenant_id", table_name="agent_lifecycle")
    op.drop_table("agent_lifecycle")
