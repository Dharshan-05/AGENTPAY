"""approval_decisions

Revision ID: 030_approval_decisions
Revises: 029_approval_requests
Create Date: 2026-08-26 08:29:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "030_approval_decisions"
down_revision: str | None = "029_approval_requests"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "approval_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_reference", sa.String(length=100), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column(
            "decision_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "decided_at",
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
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "decision IN ('approved', 'rejected', 'abstained', 'cancelled')",
            name="ck_approval_decisions_decision",
        ),
        sa.ForeignKeyConstraint(
            ["approval_request_id"],
            ["approval_requests.id"],
            name="fk_approval_decisions_approval_request_id_approval_requests",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
            name="fk_approval_decisions_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_approval_decisions"),
        sa.UniqueConstraint(
            "tenant_id",
            "decision_reference",
            name="uq_approval_decisions_tenant_id_decision_reference",
        ),
    )
    op.create_index(
        "ix_approval_decisions_tenant_id", "approval_decisions", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_approval_decisions_approval_request_id",
        "approval_decisions",
        ["approval_request_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_decisions_reviewer_id", "approval_decisions", ["reviewer_id"], unique=False
    )
    op.create_index(
        "ix_approval_decisions_decision_reference",
        "approval_decisions",
        ["decision_reference"],
        unique=False,
    )
    op.create_index(
        "ix_approval_decisions_decision", "approval_decisions", ["decision"], unique=False
    )
    op.create_index(
        "ix_approval_decisions_request_id", "approval_decisions", ["request_id"], unique=False
    )
    op.create_index(
        "ix_approval_decisions_decided_at", "approval_decisions", ["decided_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_approval_decisions_decided_at", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_request_id", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_decision", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_decision_reference", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_reviewer_id", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_approval_request_id", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_tenant_id", table_name="approval_decisions")
    op.drop_table("approval_decisions")
