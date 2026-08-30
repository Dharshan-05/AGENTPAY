"""attack_simulations

Revision ID: 034_attack_simulations
Revises: 033_security_events
Create Date: 2026-08-26 08:37:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "034_attack_simulations"
down_revision: str | None = "033_security_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "attack_simulations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("simulation_reference", sa.String(length=100), nullable=False),
        sa.Column(
            "simulation_type", sa.String(length=50), nullable=False, server_default="policy_bypass"
        ),
        sa.Column("scenario", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="planned"),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("outcome", sa.String(length=50), nullable=False, server_default="blocked"),
        sa.Column("target_component", sa.String(length=100), nullable=False),
        sa.Column("target_resource_type", sa.String(length=100), nullable=True),
        sa.Column("target_resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("initiated_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column(
            "simulation_parameters",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("expected_result", sa.String(length=50), nullable=False),
        sa.Column("actual_result", sa.String(length=50), nullable=True),
        sa.Column("findings", sa.String(length=1000), nullable=True),
        sa.Column(
            "evidence_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("risk_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "simulation_type IN ('authentication_bypass', 'authorization_bypass', "
            "'tenant_isolation', 'policy_bypass', 'fraud_detection', 'risk_manipulation', "
            "'replay', 'webhook_abuse', 'rate_limit', 'credential_abuse', 'payment_abuse')",
            name="ck_attack_simulations_simulation_type",
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'queued', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_attack_simulations_status",
        ),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_attack_simulations_severity",
        ),
        sa.CheckConstraint(
            "outcome IN ('passed', 'failed', 'blocked', 'detected', 'undetected', 'inconclusive')",
            name="ck_attack_simulations_outcome",
        ),
        sa.CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="ck_attack_simulations_risk_score",
        ),
        sa.CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_attack_simulations_confidence_score",
        ),
        sa.ForeignKeyConstraint(
            ["initiated_by"],
            ["users.id"],
            name="fk_attack_simulations_initiated_by_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attack_simulations"),
        sa.UniqueConstraint(
            "tenant_id",
            "simulation_reference",
            name="uq_attack_simulations_tenant_id_simulation_reference",
        ),
    )
    op.create_index(
        "ix_attack_simulations_tenant_id", "attack_simulations", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_attack_simulations_simulation_reference",
        "attack_simulations",
        ["simulation_reference"],
        unique=False,
    )
    op.create_index(
        "ix_attack_simulations_simulation_type",
        "attack_simulations",
        ["simulation_type"],
        unique=False,
    )
    op.create_index("ix_attack_simulations_status", "attack_simulations", ["status"], unique=False)
    op.create_index(
        "ix_attack_simulations_severity", "attack_simulations", ["severity"], unique=False
    )
    op.create_index(
        "ix_attack_simulations_outcome", "attack_simulations", ["outcome"], unique=False
    )
    op.create_index(
        "ix_attack_simulations_target_resource_id",
        "attack_simulations",
        ["target_resource_id"],
        unique=False,
    )
    op.create_index(
        "ix_attack_simulations_initiated_by", "attack_simulations", ["initiated_by"], unique=False
    )
    op.create_index(
        "ix_attack_simulations_request_id", "attack_simulations", ["request_id"], unique=False
    )
    op.create_index(
        "ix_attack_simulations_started_at", "attack_simulations", ["started_at"], unique=False
    )
    op.create_index(
        "ix_attack_simulations_completed_at", "attack_simulations", ["completed_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_attack_simulations_completed_at", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_started_at", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_request_id", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_initiated_by", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_target_resource_id", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_outcome", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_severity", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_status", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_simulation_type", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_simulation_reference", table_name="attack_simulations")
    op.drop_index("ix_attack_simulations_tenant_id", table_name="attack_simulations")
    op.drop_table("attack_simulations")
