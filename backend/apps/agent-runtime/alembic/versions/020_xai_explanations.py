"""xai_explanations

Revision ID: 020_xai_explanations
Revises: 019_fraud_predictions
Create Date: 2026-08-25 23:47:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "020_xai_explanations"
down_revision: str | None = "019_fraud_predictions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "xai_explanations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fraud_prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("risk_signal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_violation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("explanation_reference", sa.String(length=100), nullable=False),
        sa.Column("explanation_type", sa.String(length=50), nullable=False),
        sa.Column(
            "explanation_status", sa.String(length=50), nullable=False, server_default="completed"
        ),
        sa.Column("model_reference", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("explainer_type", sa.String(length=50), nullable=False),
        sa.Column("base_value", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("prediction_value", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("top_feature_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "feature_importance",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "shap_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "feature_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "explanation_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "explanation_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("summary", sa.String(length=255), nullable=True),
        sa.Column("reasoning_summary", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "generated_at",
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
            "explanation_type IN ('shap', 'feature_importance', 'counterfactual', "
            "'local', 'global', 'hybrid', 'custom')",
            name="ck_xai_explanations_explanation_type",
        ),
        sa.CheckConstraint(
            "explanation_status IN ('pending', 'completed', 'failed', 'expired', 'cancelled')",
            name="ck_xai_explanations_explanation_status",
        ),
        sa.CheckConstraint(
            "explainer_type IN ('tree_shap', 'kernel_shap', 'linear_shap', "
            "'deep_shap', 'generic_feature_importance', 'custom')",
            name="ck_xai_explanations_explainer_type",
        ),
        sa.CheckConstraint(
            "top_feature_count >= 0",
            name="ck_xai_explanations_top_feature_count_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_xai_explanations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_xai_expl_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fraud_prediction_id"],
            ["fraud_predictions.id"],
            name="fk_xai_explanations_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_xai_explanations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_xai_explanations_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_xai_explanations_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_xai_explanations_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_xai_explanations_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_xai_explanations_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["risk_signal_id"],
            ["risk_signals.id"],
            name="fk_xai_explanations_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_xai_explanations_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_xai_explanations"),
        sa.UniqueConstraint(
            "tenant_id",
            "explanation_reference",
            name="uq_xai_explanations_tenant_id_explanation_reference",
        ),
    )
    op.create_index(
        "ix_xai_explanations_tenant_id", "xai_explanations", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_xai_explanations_fraud_prediction_id",
        "xai_explanations",
        ["fraud_prediction_id"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_risk_signal_id", "xai_explanations", ["risk_signal_id"], unique=False
    )
    op.create_index(
        "ix_xai_explanations_security_violation_id",
        "xai_explanations",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_policy_evaluation_id",
        "xai_explanations",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index("ix_xai_explanations_agent_id", "xai_explanations", ["agent_id"], unique=False)
    op.create_index(
        "ix_xai_explanations_merchant_id", "xai_explanations", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_xai_explanations_product_id", "xai_explanations", ["product_id"], unique=False
    )
    op.create_index("ix_xai_explanations_offer_id", "xai_explanations", ["offer_id"], unique=False)
    op.create_index(
        "ix_xai_explanations_purchase_intent_id",
        "xai_explanations",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_purchase_plan_id",
        "xai_explanations",
        ["purchase_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_commerce_transaction_id",
        "xai_explanations",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_explanation_type",
        "xai_explanations",
        ["explanation_type"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_explanation_status",
        "xai_explanations",
        ["explanation_status"],
        unique=False,
    )
    op.create_index(
        "ix_xai_explanations_model_reference", "xai_explanations", ["model_reference"], unique=False
    )
    op.create_index(
        "ix_xai_explanations_request_id", "xai_explanations", ["request_id"], unique=False
    )
    op.create_index(
        "ix_xai_explanations_generated_at", "xai_explanations", ["generated_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_xai_explanations_generated_at", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_request_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_model_reference", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_explanation_status", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_explanation_type", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_commerce_transaction_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_purchase_plan_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_purchase_intent_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_offer_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_product_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_merchant_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_agent_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_policy_evaluation_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_security_violation_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_risk_signal_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_fraud_prediction_id", table_name="xai_explanations")
    op.drop_index("ix_xai_explanations_tenant_id", table_name="xai_explanations")
    op.drop_table("xai_explanations")
