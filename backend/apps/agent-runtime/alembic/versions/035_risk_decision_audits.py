"""risk_decision_audits

Revision ID: 035_risk_decision_audits
Revises: 034_attack_simulations
Create Date: 2026-08-26 08:38:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "035_risk_decision_audits"
down_revision: str | None = "034_attack_simulations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "risk_decision_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_reference", sa.String(length=100), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column(
            "decision_type", sa.String(length=50), nullable=False, server_default="transaction"
        ),
        sa.Column("decision", sa.String(length=50), nullable=False, server_default="allow"),
        sa.Column("result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column(
            "decision_source", sa.String(length=50), nullable=False, server_default="risk_engine"
        ),
        sa.Column("risk_score", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("confidence_score", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("risk_signal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("fraud_prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_violation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decision_reason", sa.String(length=500), nullable=True),
        sa.Column(
            "decision_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "input_summary",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "output_summary",
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
            "decision_type IN ('authorization', 'transaction', 'fraud', 'risk', "
            "'payment', 'commerce', 'spending', 'agent', 'security')",
            name="ck_risk_decision_audits_decision_type",
        ),
        sa.CheckConstraint(
            "decision IN ('allow', 'deny', 'challenge', 'review', 'block', 'require_approval')",
            name="ck_risk_decision_audits_decision",
        ),
        sa.CheckConstraint(
            "result IN ('success', 'failure', 'error', 'skipped')",
            name="ck_risk_decision_audits_result",
        ),
        sa.CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="ck_risk_decision_audits_risk_score",
        ),
        sa.CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="ck_risk_decision_audits_confidence_score",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_risk_decision_audits_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_risk_dec_audits_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fraud_prediction_id"],
            ["fraud_predictions.id"],
            name="fk_risk_decision_audits_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_risk_decision_audits_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_risk_dec_audits_pay_tx_id_pay_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_risk_decision_audits_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_risk_decision_audits_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["risk_signal_id"],
            ["risk_signals.id"],
            name="fk_risk_decision_audits_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_risk_decision_audits_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_risk_dec_audits_sec_viol_id_sec_viol",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_risk_decision_audits"),
        sa.UniqueConstraint(
            "tenant_id",
            "decision_reference",
            name="uq_risk_decision_audits_tenant_id_decision_reference",
        ),
    )
    op.create_index(
        "ix_risk_decision_audits_tenant_id", "risk_decision_audits", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_decision_reference",
        "risk_decision_audits",
        ["decision_reference"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_request_id", "risk_decision_audits", ["request_id"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_decision_type",
        "risk_decision_audits",
        ["decision_type"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_decision", "risk_decision_audits", ["decision"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_result", "risk_decision_audits", ["result"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_decision_source",
        "risk_decision_audits",
        ["decision_source"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_model_name", "risk_decision_audits", ["model_name"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_policy_evaluation_id",
        "risk_decision_audits",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_security_policy_id",
        "risk_decision_audits",
        ["security_policy_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_policy_rule_id",
        "risk_decision_audits",
        ["policy_rule_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_risk_signal_id",
        "risk_decision_audits",
        ["risk_signal_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_fraud_prediction_id",
        "risk_decision_audits",
        ["fraud_prediction_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_security_violation_id",
        "risk_decision_audits",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_agent_id", "risk_decision_audits", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_merchant_id", "risk_decision_audits", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_risk_decision_audits_commerce_transaction_id",
        "risk_decision_audits",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_payment_transaction_id",
        "risk_decision_audits",
        ["payment_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_occurred_at", "risk_decision_audits", ["occurred_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_risk_decision_audits_occurred_at", table_name="risk_decision_audits")
    op.drop_index(
        "ix_risk_decision_audits_payment_transaction_id", table_name="risk_decision_audits"
    )
    op.drop_index(
        "ix_risk_decision_audits_commerce_transaction_id", table_name="risk_decision_audits"
    )
    op.drop_index("ix_risk_decision_audits_merchant_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_agent_id", table_name="risk_decision_audits")
    op.drop_index(
        "ix_risk_decision_audits_security_violation_id", table_name="risk_decision_audits"
    )
    op.drop_index("ix_risk_decision_audits_fraud_prediction_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_risk_signal_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_policy_rule_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_security_policy_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_policy_evaluation_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_model_name", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_decision_source", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_result", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_decision", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_decision_type", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_request_id", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_decision_reference", table_name="risk_decision_audits")
    op.drop_index("ix_risk_decision_audits_tenant_id", table_name="risk_decision_audits")
    op.drop_table("risk_decision_audits")
