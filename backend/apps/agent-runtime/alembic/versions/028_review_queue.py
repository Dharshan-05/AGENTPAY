"""review_queue

Revision ID: 028_review_queue
Revises: 027_payment_idempotency_keys
Create Date: 2026-08-26 08:24:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "028_review_queue"
down_revision: str | None = "027_payment_idempotency_keys"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "review_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_reference", sa.String(length=100), nullable=False),
        sa.Column("review_type", sa.String(length=50), nullable=False, server_default="security"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="queued"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_violation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("risk_signal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("fraud_prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_reviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "review_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("decision", sa.String(length=50), nullable=True),
        sa.Column("decision_reason", sa.String(length=500), nullable=True),
        sa.Column(
            "queued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(
            "review_type IN ('security', 'risk', 'fraud', 'payment', 'transaction', "
            "'authorization', 'compliance', 'manual', 'agent', 'commerce')",
            name="ck_review_queue_review_type",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'assigned', 'in_review', 'approved', 'rejected', "
            "'escalated', 'resolved', 'cancelled')",
            name="ck_review_queue_status",
        ),
        sa.CheckConstraint("priority >= 0", name="ck_review_queue_priority_nonnegative"),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')", name="ck_review_queue_severity"
        ),
        sa.CheckConstraint(
            "decision IS NULL OR decision IN ('allow', 'deny', 'approve', 'reject', "
            "'escalate', 'cancel', 'review')",
            name="ck_review_queue_decision",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_review_queue_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_reviewer_id"],
            ["users.id"],
            name="fk_review_queue_assigned_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_review_queue_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fraud_prediction_id"],
            ["fraud_predictions.id"],
            name="fk_review_queue_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_review_queue_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_review_queue_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_review_queue_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_review_queue_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_review_queue_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["risk_signal_id"],
            ["risk_signals.id"],
            name="fk_review_queue_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_review_queue_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_review_queue_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_review_queue"),
        sa.UniqueConstraint(
            "tenant_id",
            "review_reference",
            name="uq_review_queue_tenant_id_review_reference",
        ),
    )
    op.create_index("ix_review_queue_tenant_id", "review_queue", ["tenant_id"], unique=False)
    op.create_index(
        "ix_review_queue_review_reference", "review_queue", ["review_reference"], unique=False
    )
    op.create_index("ix_review_queue_status", "review_queue", ["status"], unique=False)
    op.create_index("ix_review_queue_priority", "review_queue", ["priority"], unique=False)
    op.create_index("ix_review_queue_severity", "review_queue", ["severity"], unique=False)
    op.create_index("ix_review_queue_review_type", "review_queue", ["review_type"], unique=False)
    op.create_index(
        "ix_review_queue_assigned_reviewer_id",
        "review_queue",
        ["assigned_reviewer_id"],
        unique=False,
    )
    op.create_index("ix_review_queue_request_id", "review_queue", ["request_id"], unique=False)
    op.create_index("ix_review_queue_queued_at", "review_queue", ["queued_at"], unique=False)
    op.create_index("ix_review_queue_source_id", "review_queue", ["source_id"], unique=False)
    op.create_index(
        "ix_review_queue_security_policy_id", "review_queue", ["security_policy_id"], unique=False
    )
    op.create_index(
        "ix_review_queue_policy_rule_id", "review_queue", ["policy_rule_id"], unique=False
    )
    op.create_index(
        "ix_review_queue_policy_evaluation_id",
        "review_queue",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_review_queue_security_violation_id",
        "review_queue",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index(
        "ix_review_queue_risk_signal_id", "review_queue", ["risk_signal_id"], unique=False
    )
    op.create_index(
        "ix_review_queue_fraud_prediction_id", "review_queue", ["fraud_prediction_id"], unique=False
    )
    op.create_index(
        "ix_review_queue_commerce_transaction_id",
        "review_queue",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_review_queue_payment_order_id", "review_queue", ["payment_order_id"], unique=False
    )
    op.create_index(
        "ix_review_queue_payment_transaction_id",
        "review_queue",
        ["payment_transaction_id"],
        unique=False,
    )
    op.create_index("ix_review_queue_agent_id", "review_queue", ["agent_id"], unique=False)
    op.create_index("ix_review_queue_merchant_id", "review_queue", ["merchant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_review_queue_merchant_id", table_name="review_queue")
    op.drop_index("ix_review_queue_agent_id", table_name="review_queue")
    op.drop_index("ix_review_queue_payment_transaction_id", table_name="review_queue")
    op.drop_index("ix_review_queue_payment_order_id", table_name="review_queue")
    op.drop_index("ix_review_queue_commerce_transaction_id", table_name="review_queue")
    op.drop_index("ix_review_queue_fraud_prediction_id", table_name="review_queue")
    op.drop_index("ix_review_queue_risk_signal_id", table_name="review_queue")
    op.drop_index("ix_review_queue_security_violation_id", table_name="review_queue")
    op.drop_index("ix_review_queue_policy_evaluation_id", table_name="review_queue")
    op.drop_index("ix_review_queue_policy_rule_id", table_name="review_queue")
    op.drop_index("ix_review_queue_security_policy_id", table_name="review_queue")
    op.drop_index("ix_review_queue_source_id", table_name="review_queue")
    op.drop_index("ix_review_queue_queued_at", table_name="review_queue")
    op.drop_index("ix_review_queue_request_id", table_name="review_queue")
    op.drop_index("ix_review_queue_assigned_reviewer_id", table_name="review_queue")
    op.drop_index("ix_review_queue_review_type", table_name="review_queue")
    op.drop_index("ix_review_queue_severity", table_name="review_queue")
    op.drop_index("ix_review_queue_priority", table_name="review_queue")
    op.drop_index("ix_review_queue_status", table_name="review_queue")
    op.drop_index("ix_review_queue_review_reference", table_name="review_queue")
    op.drop_index("ix_review_queue_tenant_id", table_name="review_queue")
    op.drop_table("review_queue")
