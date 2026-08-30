"""fraud_predictions

Revision ID: 019_fraud_predictions
Revises: 018_security_violations_and_risk_signals
Create Date: 2026-08-25 23:46:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "019_fraud_predictions"
down_revision: str | None = "018_security_violations_and_risk_signals"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fraud_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_violation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("risk_signal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("prediction_reference", sa.String(length=100), nullable=False),
        sa.Column("model_reference", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("prediction_type", sa.String(length=50), nullable=False),
        sa.Column(
            "prediction_status", sa.String(length=50), nullable=False, server_default="completed"
        ),
        sa.Column("prediction_label", sa.String(length=50), nullable=False),
        sa.Column("fraud_probability", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("legitimate_probability", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("risk_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("feature_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "feature_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "prediction_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "prediction_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "predicted_at",
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "prediction_type IN ('transaction', 'payment', 'purchase', 'account', "
            "'agent', 'merchant', 'identity', 'behaviour', 'commerce', 'custom')",
            name="ck_fraud_predictions_prediction_type",
        ),
        sa.CheckConstraint(
            "prediction_status IN ('pending', 'completed', 'failed', 'expired', 'cancelled')",
            name="ck_fraud_predictions_prediction_status",
        ),
        sa.CheckConstraint(
            "prediction_label IN ('legitimate', 'suspicious', 'fraud', 'unknown')",
            name="ck_fraud_predictions_prediction_label",
        ),
        sa.CheckConstraint(
            "fraud_probability IS NULL OR (fraud_probability >= 0 AND fraud_probability <= 1)",
            name="ck_fraud_predictions_fraud_probability_bounds",
        ),
        sa.CheckConstraint(
            "legitimate_probability IS NULL OR (legitimate_probability >= 0 AND legitimate_probability <= 1)",  # noqa: E501
            name="ck_fraud_predictions_legitimate_probability_bounds",
        ),
        sa.CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="ck_fraud_predictions_risk_score_bounds",
        ),
        sa.CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_fraud_predictions_confidence_score_bounds",
        ),
        sa.CheckConstraint(
            "feature_count >= 0",
            name="ck_fraud_predictions_feature_count_nonnegative",
        ),
        sa.CheckConstraint(
            "fraud_probability IS NULL OR legitimate_probability IS NULL OR "
            "(fraud_probability + legitimate_probability BETWEEN 0.99 AND 1.01)",
            name="ck_fraud_predictions_probability_consistency",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_fraud_predictions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_fraud_pred_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_fraud_predictions_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_fraud_predictions_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_fraud_predictions_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_fraud_predictions_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_fraud_predictions_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_fraud_predictions_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_fraud_predictions_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["risk_signal_id"],
            ["risk_signals.id"],
            name="fk_fraud_predictions_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_fraud_predictions_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_fraud_predictions_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_fraud_predictions"),
        sa.UniqueConstraint(
            "tenant_id",
            "prediction_reference",
            name="uq_fraud_predictions_tenant_id_prediction_reference",
        ),
    )
    op.create_index(
        "ix_fraud_predictions_tenant_id", "fraud_predictions", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_security_policy_id",
        "fraud_predictions",
        ["security_policy_id"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_policy_rule_id", "fraud_predictions", ["policy_rule_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_policy_evaluation_id",
        "fraud_predictions",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_security_violation_id",
        "fraud_predictions",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_risk_signal_id", "fraud_predictions", ["risk_signal_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_agent_id", "fraud_predictions", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_merchant_id", "fraud_predictions", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_product_id", "fraud_predictions", ["product_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_offer_id", "fraud_predictions", ["offer_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_purchase_intent_id",
        "fraud_predictions",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_purchase_plan_id",
        "fraud_predictions",
        ["purchase_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_commerce_transaction_id",
        "fraud_predictions",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_prediction_type",
        "fraud_predictions",
        ["prediction_type"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_prediction_status",
        "fraud_predictions",
        ["prediction_status"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_prediction_label",
        "fraud_predictions",
        ["prediction_label"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_model_reference",
        "fraud_predictions",
        ["model_reference"],
        unique=False,
    )
    op.create_index(
        "ix_fraud_predictions_request_id", "fraud_predictions", ["request_id"], unique=False
    )
    op.create_index(
        "ix_fraud_predictions_predicted_at", "fraud_predictions", ["predicted_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_fraud_predictions_predicted_at", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_request_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_model_reference", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_prediction_label", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_prediction_status", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_prediction_type", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_commerce_transaction_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_purchase_plan_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_purchase_intent_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_offer_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_product_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_merchant_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_agent_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_risk_signal_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_security_violation_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_policy_evaluation_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_policy_rule_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_security_policy_id", table_name="fraud_predictions")
    op.drop_index("ix_fraud_predictions_tenant_id", table_name="fraud_predictions")
    op.drop_table("fraud_predictions")
