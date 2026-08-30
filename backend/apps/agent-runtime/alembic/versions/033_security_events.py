"""security_events

Revision ID: 033_security_events
Revises: 032_global_audit_logs
Create Date: 2026-08-26 08:36:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "033_security_events"
down_revision: str | None = "032_global_audit_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "security_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_reference", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False, server_default="system"),
        sa.Column(
            "event_action", sa.String(length=50), nullable=False, server_default="security_alert"
        ),
        sa.Column("event_result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="internal"),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=50), nullable=False, server_default="user"),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_violation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("risk_signal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "event_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
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
        sa.CheckConstraint(
            "event_type IN ('authentication', 'authorization', 'policy', 'credential', "
            "'tenant_isolation', 'suspicious_activity', 'security_control', 'attack', 'system')",
            name="ck_security_events_event_type",
        ),
        sa.CheckConstraint(
            "event_action IN ('login', 'logout', 'authentication_failed', 'authorization_denied', "
            "'permission_changed', 'credential_used', 'credential_failed', 'policy_blocked', "
            "'policy_violation', 'tenant_boundary_violation', 'suspicious_request', "
            "'attack_detected', 'security_control_triggered', 'security_alert', 'security_reviewed')",  # noqa: E501
            name="ck_security_events_event_action",
        ),
        sa.CheckConstraint(
            "event_result IN ('success', 'failure', 'blocked', 'detected', 'review_required', 'error')",  # noqa: E501
            name="ck_security_events_event_result",
        ),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_security_events_severity",
        ),
        sa.CheckConstraint(
            "source IN ('internal', 'external', 'agent', 'merchant', 'webhook', "
            "'policy_engine', 'risk_engine', 'siem', 'system')",
            name="ck_security_events_source",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_security_events_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_security_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_security_events_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["risk_signal_id"],
            ["risk_signals.id"],
            name="fk_security_events_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_security_events_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_security_events_user_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_security_events"),
        sa.UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_security_events_tenant_id_event_reference",
        ),
    )
    op.create_index("ix_security_events_tenant_id", "security_events", ["tenant_id"], unique=False)
    op.create_index(
        "ix_security_events_event_reference", "security_events", ["event_reference"], unique=False
    )
    op.create_index(
        "ix_security_events_event_type", "security_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_security_events_event_action", "security_events", ["event_action"], unique=False
    )
    op.create_index(
        "ix_security_events_event_result", "security_events", ["event_result"], unique=False
    )
    op.create_index("ix_security_events_severity", "security_events", ["severity"], unique=False)
    op.create_index("ix_security_events_source", "security_events", ["source"], unique=False)
    op.create_index(
        "ix_security_events_request_id", "security_events", ["request_id"], unique=False
    )
    op.create_index("ix_security_events_actor_id", "security_events", ["actor_id"], unique=False)
    op.create_index("ix_security_events_user_id", "security_events", ["user_id"], unique=False)
    op.create_index("ix_security_events_agent_id", "security_events", ["agent_id"], unique=False)
    op.create_index(
        "ix_security_events_merchant_id", "security_events", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_security_events_security_violation_id",
        "security_events",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_events_risk_signal_id", "security_events", ["risk_signal_id"], unique=False
    )
    op.create_index(
        "ix_security_events_policy_evaluation_id",
        "security_events",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_events_occurred_at", "security_events", ["occurred_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_security_events_occurred_at", table_name="security_events")
    op.drop_index("ix_security_events_policy_evaluation_id", table_name="security_events")
    op.drop_index("ix_security_events_risk_signal_id", table_name="security_events")
    op.drop_index("ix_security_events_security_violation_id", table_name="security_events")
    op.drop_index("ix_security_events_merchant_id", table_name="security_events")
    op.drop_index("ix_security_events_agent_id", table_name="security_events")
    op.drop_index("ix_security_events_user_id", table_name="security_events")
    op.drop_index("ix_security_events_actor_id", table_name="security_events")
    op.drop_index("ix_security_events_request_id", table_name="security_events")
    op.drop_index("ix_security_events_source", table_name="security_events")
    op.drop_index("ix_security_events_severity", table_name="security_events")
    op.drop_index("ix_security_events_event_result", table_name="security_events")
    op.drop_index("ix_security_events_event_action", table_name="security_events")
    op.drop_index("ix_security_events_event_type", table_name="security_events")
    op.drop_index("ix_security_events_event_reference", table_name="security_events")
    op.drop_index("ix_security_events_tenant_id", table_name="security_events")
    op.drop_table("security_events")
