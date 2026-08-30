"""approval_requests

Revision ID: 029_approval_requests
Revises: 028_review_queue
Create Date: 2026-08-26 08:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "029_approval_requests"
down_revision: str | None = "028_review_queue"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "approval_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approval_reference", sa.String(length=100), nullable=False),
        sa.Column("approval_type", sa.String(length=50), nullable=False, server_default="payment"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "requested_action", sa.String(length=50), nullable=False, server_default="authorize"
        ),
        sa.Column("requested_amount", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("requester_type", sa.String(length=100), nullable=True),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_reviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("required_approvals", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("received_approvals", sa.Integer(), nullable=False, server_default="0"),
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
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "approval_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
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
            "approval_type IN ('payment', 'transaction', 'refund', 'cancellation', "
            "'security', 'risk', 'fraud', 'commerce', 'agent', 'policy', 'manual')",
            name="ck_approval_requests_approval_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'in_review', 'partially_approved', 'approved', "
            "'rejected', 'expired', 'cancelled')",
            name="ck_approval_requests_status",
        ),
        sa.CheckConstraint(
            "requested_action IN ('authorize', 'capture', 'refund', 'cancel', "
            "'execute', 'allow', 'deny', 'override', 'escalate')",
            name="ck_approval_requests_requested_action",
        ),
        sa.CheckConstraint("priority >= 0", name="ck_approval_requests_priority_nonnegative"),
        sa.CheckConstraint(
            "requested_amount IS NULL OR requested_amount >= 0",
            name="ck_approval_requests_requested_amount_nonnegative",
        ),
        sa.CheckConstraint(
            "required_approvals > 0", name="ck_approval_requests_required_approvals_positive"
        ),
        sa.CheckConstraint(
            "received_approvals >= 0", name="ck_approval_requests_received_approvals_nonnegative"
        ),
        sa.CheckConstraint(
            "received_approvals <= required_approvals",
            name="ck_approval_requests_received_le_required",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_approval_requests_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_appr_req_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fraud_prediction_id"],
            ["fraud_predictions.id"],
            name="fk_approval_requests_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_approval_requests_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_approval_requests_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_appr_req_pay_tx_id_pay_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_approval_requests_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_approval_requests_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requester_id"],
            ["users.id"],
            name="fk_approval_requests_requester_id_users",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["risk_signal_id"],
            ["risk_signals.id"],
            name="fk_approval_requests_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_approval_requests_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_approval_requests_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["target_reviewer_id"],
            ["users.id"],
            name="fk_approval_requests_target_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_approval_requests"),
        sa.UniqueConstraint(
            "tenant_id",
            "approval_reference",
            name="uq_approval_requests_tenant_id_approval_reference",
        ),
    )
    op.create_index(
        "ix_approval_requests_tenant_id", "approval_requests", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_approval_reference",
        "approval_requests",
        ["approval_reference"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_approval_type", "approval_requests", ["approval_type"], unique=False
    )
    op.create_index("ix_approval_requests_status", "approval_requests", ["status"], unique=False)
    op.create_index(
        "ix_approval_requests_priority", "approval_requests", ["priority"], unique=False
    )
    op.create_index(
        "ix_approval_requests_requester_id", "approval_requests", ["requester_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_target_reviewer_id",
        "approval_requests",
        ["target_reviewer_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_request_id", "approval_requests", ["request_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_expires_at", "approval_requests", ["expires_at"], unique=False
    )
    op.create_index(
        "ix_approval_requests_requested_at", "approval_requests", ["requested_at"], unique=False
    )
    op.create_index(
        "ix_approval_requests_source_id", "approval_requests", ["source_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_security_policy_id",
        "approval_requests",
        ["security_policy_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_policy_rule_id", "approval_requests", ["policy_rule_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_policy_evaluation_id",
        "approval_requests",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_security_violation_id",
        "approval_requests",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_risk_signal_id", "approval_requests", ["risk_signal_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_fraud_prediction_id",
        "approval_requests",
        ["fraud_prediction_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_commerce_transaction_id",
        "approval_requests",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_payment_order_id",
        "approval_requests",
        ["payment_order_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_payment_transaction_id",
        "approval_requests",
        ["payment_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_agent_id", "approval_requests", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_approval_requests_merchant_id", "approval_requests", ["merchant_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_approval_requests_merchant_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_agent_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_payment_transaction_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_payment_order_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_commerce_transaction_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_fraud_prediction_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_risk_signal_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_security_violation_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_policy_evaluation_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_policy_rule_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_security_policy_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_source_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_requested_at", table_name="approval_requests")
    op.drop_index("ix_approval_requests_expires_at", table_name="approval_requests")
    op.drop_index("ix_approval_requests_request_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_target_reviewer_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_requester_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_priority", table_name="approval_requests")
    op.drop_index("ix_approval_requests_status", table_name="approval_requests")
    op.drop_index("ix_approval_requests_approval_type", table_name="approval_requests")
    op.drop_index("ix_approval_requests_approval_reference", table_name="approval_requests")
    op.drop_index("ix_approval_requests_tenant_id", table_name="approval_requests")
    op.drop_table("approval_requests")
