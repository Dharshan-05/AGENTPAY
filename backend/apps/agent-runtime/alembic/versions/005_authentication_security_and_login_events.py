"""authentication_security_and_login_events

Revision ID: 005_auth_security_events
Revises: 004_auth_sessions_tokens
Create Date: 2026-08-25 21:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_auth_security_events"
down_revision: str | None = "004_auth_sessions_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create authentication_security table
    op.create_table(
        "authentication_security",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_successful_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failed_login_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(
            "failed_login_attempts >= 0",
            name="ck_authentication_security_failed_login_attempts_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_authentication_security_user_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_authentication_security"),
        sa.UniqueConstraint("user_id", name="uq_authentication_security_user_id"),
    )
    op.create_index(
        "ix_authentication_security_tenant_id",
        "authentication_security",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_authentication_security_user_id", "authentication_security", ["user_id"], unique=False
    )
    op.create_index(
        "ix_authentication_security_status", "authentication_security", ["status"], unique=False
    )
    op.create_index(
        "ix_authentication_security_locked_until",
        "authentication_security",
        ["locked_until"],
        unique=False,
    )

    # 2. Create login_security_events table
    op.create_table(
        "login_security_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("refresh_token_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(length=255), nullable=True),
        sa.Column(
            "event_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["refresh_token_id"],
            ["refresh_tokens.id"],
            name="fk_login_security_events_refresh_token_id_refresh_tokens",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name="fk_login_security_events_session_id_sessions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_login_security_events_user_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_login_security_events"),
    )
    op.create_index(
        "ix_login_security_events_tenant_id", "login_security_events", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_login_security_events_user_id", "login_security_events", ["user_id"], unique=False
    )
    op.create_index(
        "ix_login_security_events_session_id", "login_security_events", ["session_id"], unique=False
    )
    op.create_index(
        "ix_login_security_events_refresh_token_id",
        "login_security_events",
        ["refresh_token_id"],
        unique=False,
    )
    op.create_index(
        "ix_login_security_events_event_type", "login_security_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_login_security_events_occurred_at",
        "login_security_events",
        ["occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    # 1. Drop login_security_events table
    op.drop_index("ix_login_security_events_occurred_at", table_name="login_security_events")
    op.drop_index("ix_login_security_events_event_type", table_name="login_security_events")
    op.drop_index("ix_login_security_events_refresh_token_id", table_name="login_security_events")
    op.drop_index("ix_login_security_events_session_id", table_name="login_security_events")
    op.drop_index("ix_login_security_events_user_id", table_name="login_security_events")
    op.drop_index("ix_login_security_events_tenant_id", table_name="login_security_events")
    op.drop_table("login_security_events")

    # 2. Drop authentication_security table
    op.drop_index("ix_authentication_security_locked_until", table_name="authentication_security")
    op.drop_index("ix_authentication_security_status", table_name="authentication_security")
    op.drop_index("ix_authentication_security_user_id", table_name="authentication_security")
    op.drop_index("ix_authentication_security_tenant_id", table_name="authentication_security")
    op.drop_table("authentication_security")
