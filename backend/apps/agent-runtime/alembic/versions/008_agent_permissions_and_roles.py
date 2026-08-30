"""agent_permissions_and_roles

Revision ID: 008_agent_permissions_and_roles
Revises: 007_agent_credentials_and_sessions
Create Date: 2026-08-25 21:55:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008_agent_permissions_and_roles"
down_revision: str | None = "007_agent_credentials_and_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create agent_permissions table
    op.create_table(
        "agent_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_permissions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_agent_permissions_permission_id_permissions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_permissions"),
        sa.UniqueConstraint(
            "agent_id", "permission_id", name="uq_agent_permissions_agent_id_permission_id"
        ),
    )
    op.create_index(
        "ix_agent_permissions_tenant_id", "agent_permissions", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_agent_permissions_agent_id", "agent_permissions", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_agent_permissions_permission_id", "agent_permissions", ["permission_id"], unique=False
    )

    # 2. Create agent_roles table
    op.create_table(
        "agent_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_roles_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_agent_roles_role_id_roles",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_roles"),
        sa.UniqueConstraint("agent_id", "role_id", name="uq_agent_roles_agent_id_role_id"),
    )
    op.create_index("ix_agent_roles_tenant_id", "agent_roles", ["tenant_id"], unique=False)
    op.create_index("ix_agent_roles_agent_id", "agent_roles", ["agent_id"], unique=False)
    op.create_index("ix_agent_roles_role_id", "agent_roles", ["role_id"], unique=False)


def downgrade() -> None:
    # 1. Drop agent_roles table
    op.drop_index("ix_agent_roles_role_id", table_name="agent_roles")
    op.drop_index("ix_agent_roles_agent_id", table_name="agent_roles")
    op.drop_index("ix_agent_roles_tenant_id", table_name="agent_roles")
    op.drop_table("agent_roles")

    # 2. Drop agent_permissions table
    op.drop_index("ix_agent_permissions_permission_id", table_name="agent_permissions")
    op.drop_index("ix_agent_permissions_agent_id", table_name="agent_permissions")
    op.drop_index("ix_agent_permissions_tenant_id", table_name="agent_permissions")
    op.drop_table("agent_permissions")
