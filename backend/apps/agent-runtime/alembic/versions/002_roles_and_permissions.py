"""roles_and_permissions

Revision ID: 002_roles_and_permissions
Revises: 001_identity_users
Create Date: 2026-08-25 20:55:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_roles_and_permissions"
down_revision: str | None = "001_identity_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create roles table
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
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
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_id_name"),
    )
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"], unique=False)
    op.create_index("ix_roles_name", "roles", ["name"], unique=False)

    # 2. Create permissions table
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
        sa.UniqueConstraint("name", name="uq_permissions_name"),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"], unique=False)
    op.create_index("ix_permissions_resource", "permissions", ["resource"], unique=False)


def downgrade() -> None:
    # 1. Drop permissions table
    op.drop_index("ix_permissions_resource", table_name="permissions")
    op.drop_index("ix_permissions_name", table_name="permissions")
    op.drop_table("permissions")

    # 2. Drop roles table
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_index("ix_roles_tenant_id", table_name="roles")
    op.drop_table("roles")
