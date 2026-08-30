"""agents_and_agent_identity

Revision ID: 006_agents_and_agent_identity
Revises: 005_auth_security_events
Create Date: 2026-08-25 21:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_agents_and_agent_identity"
down_revision: str | None = "005_auth_security_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create agents table
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("agent_type", sa.String(length=50), nullable=False, server_default="autonomous"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_agents"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_agents_tenant_id_slug"),
    )
    op.create_index("ix_agents_tenant_id", "agents", ["tenant_id"], unique=False)
    op.create_index("ix_agents_slug", "agents", ["slug"], unique=False)
    op.create_index("ix_agents_status", "agents", ["status"], unique=False)

    # 2. Create agent_identities table
    op.create_table(
        "agent_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("identity_type", sa.String(length=50), nullable=False, server_default="standard"),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
            name="fk_agent_identities_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_identities"),
        sa.UniqueConstraint("agent_id", name="uq_agent_identities_agent_id"),
    )
    op.create_index(
        "ix_agent_identities_tenant_id", "agent_identities", ["tenant_id"], unique=False
    )
    op.create_index("ix_agent_identities_agent_id", "agent_identities", ["agent_id"], unique=False)


def downgrade() -> None:
    # 1. Drop agent_identities table
    op.drop_index("ix_agent_identities_agent_id", table_name="agent_identities")
    op.drop_index("ix_agent_identities_tenant_id", table_name="agent_identities")
    op.drop_table("agent_identities")

    # 2. Drop agents table
    op.drop_index("ix_agents_status", table_name="agents")
    op.drop_index("ix_agents_slug", table_name="agents")
    op.drop_index("ix_agents_tenant_id", table_name="agents")
    op.drop_table("agents")
