"""agent_credentials_and_sessions

Revision ID: 007_agent_credentials_and_sessions
Revises: 006_agents_and_agent_identity
Create Date: 2026-08-25 21:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007_agent_credentials_and_sessions"
down_revision: str | None = "006_agents_and_agent_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create agent_credentials table
    op.create_table(
        "agent_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credential_type", sa.String(length=50), nullable=False),
        sa.Column("credential_identifier", sa.String(length=255), nullable=True),
        sa.Column("secret_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_credential_id", postgresql.UUID(as_uuid=True), nullable=True),
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
            name="fk_agent_credentials_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_credential_id"],
            ["agent_credentials.id"],
            name="fk_agent_cred_replaced_by_cred_id_agent_cred",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_credentials"),
    )
    op.create_index(
        "ix_agent_credentials_tenant_id", "agent_credentials", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_agent_credentials_agent_id", "agent_credentials", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_agent_credentials_credential_identifier",
        "agent_credentials",
        ["credential_identifier"],
        unique=False,
    )
    op.create_index("ix_agent_credentials_status", "agent_credentials", ["status"], unique=False)
    op.create_index(
        "ix_agent_credentials_expires_at", "agent_credentials", ["expires_at"], unique=False
    )

    # 2. Create agent_sessions table
    op.create_table(
        "agent_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credential_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "session_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=255), nullable=True),
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
            name="fk_agent_sessions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["credential_id"],
            ["agent_credentials.id"],
            name="fk_agent_sessions_credential_id_agent_credentials",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_sessions"),
    )
    op.create_index("ix_agent_sessions_tenant_id", "agent_sessions", ["tenant_id"], unique=False)
    op.create_index("ix_agent_sessions_agent_id", "agent_sessions", ["agent_id"], unique=False)
    op.create_index(
        "ix_agent_sessions_credential_id", "agent_sessions", ["credential_id"], unique=False
    )
    op.create_index("ix_agent_sessions_status", "agent_sessions", ["status"], unique=False)
    op.create_index("ix_agent_sessions_expires_at", "agent_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    # 1. Drop agent_sessions table
    op.drop_index("ix_agent_sessions_expires_at", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_status", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_credential_id", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_agent_id", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_tenant_id", table_name="agent_sessions")
    op.drop_table("agent_sessions")

    # 2. Drop agent_credentials table
    op.drop_index("ix_agent_credentials_expires_at", table_name="agent_credentials")
    op.drop_index("ix_agent_credentials_status", table_name="agent_credentials")
    op.drop_index("ix_agent_credentials_credential_identifier", table_name="agent_credentials")
    op.drop_index("ix_agent_credentials_agent_id", table_name="agent_credentials")
    op.drop_index("ix_agent_credentials_tenant_id", table_name="agent_credentials")
    op.drop_table("agent_credentials")
