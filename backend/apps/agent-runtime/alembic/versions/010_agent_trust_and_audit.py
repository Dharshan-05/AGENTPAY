"""agent_trust_and_audit

Revision ID: 010_agent_trust_and_audit
Revises: 009_agent_lifecycle_and_metadata
Create Date: 2026-08-25 22:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010_agent_trust_and_audit"
down_revision: str | None = "009_agent_lifecycle_and_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create agent_trust table
    op.create_table(
        "agent_trust",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trust_status", sa.String(length=50), nullable=False, server_default="unknown"),
        sa.Column("trust_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("trust_reason", sa.String(length=255), nullable=True),
        sa.Column(
            "trust_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
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
            "trust_score IS NULL OR (trust_score >= 0 AND trust_score <= 100)",
            name="ck_agent_trust_score_range",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_trust_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_trust"),
        sa.UniqueConstraint("agent_id", name="uq_agent_trust_agent_id"),
    )
    op.create_index("ix_agent_trust_tenant_id", "agent_trust", ["tenant_id"], unique=False)
    op.create_index("ix_agent_trust_agent_id", "agent_trust", ["agent_id"], unique=False)
    op.create_index("ix_agent_trust_trust_status", "agent_trust", ["trust_status"], unique=False)

    # 2. Create agent_audit table
    op.create_table(
        "agent_audit",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_type", sa.String(length=50), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_action", sa.String(length=100), nullable=False),
        sa.Column("event_result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
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
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_agent_audit_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_agent_audit"),
    )
    op.create_index("ix_agent_audit_tenant_id", "agent_audit", ["tenant_id"], unique=False)
    op.create_index("ix_agent_audit_agent_id", "agent_audit", ["agent_id"], unique=False)
    op.create_index("ix_agent_audit_actor_type", "agent_audit", ["actor_type"], unique=False)
    op.create_index("ix_agent_audit_actor_id", "agent_audit", ["actor_id"], unique=False)
    op.create_index("ix_agent_audit_event_type", "agent_audit", ["event_type"], unique=False)
    op.create_index("ix_agent_audit_occurred_at", "agent_audit", ["occurred_at"], unique=False)


def downgrade() -> None:
    # 1. Drop agent_audit table
    op.drop_index("ix_agent_audit_occurred_at", table_name="agent_audit")
    op.drop_index("ix_agent_audit_event_type", table_name="agent_audit")
    op.drop_index("ix_agent_audit_actor_id", table_name="agent_audit")
    op.drop_index("ix_agent_audit_actor_type", table_name="agent_audit")
    op.drop_index("ix_agent_audit_agent_id", table_name="agent_audit")
    op.drop_index("ix_agent_audit_tenant_id", table_name="agent_audit")
    op.drop_table("agent_audit")

    # 2. Drop agent_trust table
    op.drop_index("ix_agent_trust_trust_status", table_name="agent_trust")
    op.drop_index("ix_agent_trust_agent_id", table_name="agent_trust")
    op.drop_index("ix_agent_trust_tenant_id", table_name="agent_trust")
    op.drop_table("agent_trust")
