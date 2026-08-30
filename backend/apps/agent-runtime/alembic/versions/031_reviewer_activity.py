"""reviewer_activity

Revision ID: 031_reviewer_activity
Revises: 030_approval_decisions
Create Date: 2026-08-26 08:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "031_reviewer_activity"
down_revision: str | None = "030_approval_decisions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reviewer_activity",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_queue_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approval_decision_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("activity_reference", sa.String(length=100), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False, server_default="review"),
        sa.Column("activity_action", sa.String(length=50), nullable=False, server_default="viewed"),
        sa.Column("actor_type", sa.String(length=50), nullable=False, server_default="user"),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column(
            "activity_payload",
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
            "activity_type IN ('review', 'approval', 'decision', 'comment', 'assignment', 'escalation', 'claim')",  # noqa: E501
            name="ck_reviewer_activity_activity_type",
        ),
        sa.CheckConstraint(
            "activity_action IN ('assigned', 'viewed', 'opened', 'claimed', 'commented', "
            "'approved', 'rejected', 'escalated', 'reassigned', 'requested_information', "
            "'released', 'skipped', 'expired')",
            name="ck_reviewer_activity_activity_action",
        ),
        sa.ForeignKeyConstraint(
            ["approval_decision_id"],
            ["approval_decisions.id"],
            name="fk_reviewer_activity_approval_decision_id_approval_decisions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["approval_request_id"],
            ["approval_requests.id"],
            name="fk_reviewer_activity_approval_request_id_approval_requests",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["review_queue_id"],
            ["review_queue.id"],
            name="fk_reviewer_activity_review_queue_id_review_queue",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
            name="fk_reviewer_activity_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reviewer_activity"),
        sa.UniqueConstraint(
            "tenant_id",
            "activity_reference",
            name="uq_reviewer_activity_tenant_id_activity_reference",
        ),
    )
    op.create_index(
        "ix_reviewer_activity_tenant_id", "reviewer_activity", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_reviewer_activity_reviewer_id", "reviewer_activity", ["reviewer_id"], unique=False
    )
    op.create_index(
        "ix_reviewer_activity_review_queue_id",
        "reviewer_activity",
        ["review_queue_id"],
        unique=False,
    )
    op.create_index(
        "ix_reviewer_activity_approval_request_id",
        "reviewer_activity",
        ["approval_request_id"],
        unique=False,
    )
    op.create_index(
        "ix_reviewer_activity_approval_decision_id",
        "reviewer_activity",
        ["approval_decision_id"],
        unique=False,
    )
    op.create_index(
        "ix_reviewer_activity_activity_reference",
        "reviewer_activity",
        ["activity_reference"],
        unique=False,
    )
    op.create_index(
        "ix_reviewer_activity_activity_type", "reviewer_activity", ["activity_type"], unique=False
    )
    op.create_index(
        "ix_reviewer_activity_activity_action",
        "reviewer_activity",
        ["activity_action"],
        unique=False,
    )
    op.create_index(
        "ix_reviewer_activity_request_id", "reviewer_activity", ["request_id"], unique=False
    )
    op.create_index(
        "ix_reviewer_activity_actor_id", "reviewer_activity", ["actor_id"], unique=False
    )
    op.create_index(
        "ix_reviewer_activity_occurred_at", "reviewer_activity", ["occurred_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_reviewer_activity_occurred_at", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_actor_id", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_request_id", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_activity_action", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_activity_type", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_activity_reference", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_approval_decision_id", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_approval_request_id", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_review_queue_id", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_reviewer_id", table_name="reviewer_activity")
    op.drop_index("ix_reviewer_activity_tenant_id", table_name="reviewer_activity")
    op.drop_table("reviewer_activity")
