"""security_violations_and_risk_signals

Revision ID: 018_security_violations_and_risk_signals
Revises: 017_policy_evaluation_and_behaviour_events
Create Date: 2026-08-25 23:38:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_security_violations_and_risk_signals"
down_revision: str | None = "017_policy_evaluation_and_behaviour_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create security_violations table
    op.create_table(
        "security_violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("violation_reference", sa.String(length=100), nullable=False),
        sa.Column("violation_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="open"),
        sa.Column("detection_source", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("violation_code", sa.String(length=100), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("risk_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("impact_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column(
            "violation_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "evidence_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "resolution_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
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
            "violation_type IN ('authentication', 'authorization', 'policy', 'fraud', "
            "'risk', 'compliance', 'spending', 'access', 'agent', 'commerce', "
            "'transaction', 'inventory', 'credential', 'tenant_isolation', 'system')",
            name="ck_security_violations_violation_type",
        ),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_security_violations_severity",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'investigating', 'confirmed', 'resolved', "
            "'dismissed', 'false_positive')",
            name="ck_security_violations_status",
        ),
        sa.CheckConstraint(
            "detection_source IN ('policy_engine', 'rule_engine', 'risk_engine', "
            "'fraud_engine', 'authentication', 'authorization', 'agent_runtime', "
            "'system', 'manual')",
            name="ck_security_violations_detection_source",
        ),
        sa.CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="ck_security_violations_risk_score_bounds",
        ),
        sa.CheckConstraint(
            "impact_score IS NULL OR (impact_score >= 0 AND impact_score <= 100)",
            name="ck_security_violations_impact_score_bounds",
        ),
        sa.CheckConstraint(
            "acknowledged_at IS NULL OR detected_at <= acknowledged_at",
            name="ck_security_violations_acknowledged_bounds",
        ),
        sa.CheckConstraint(
            "resolved_at IS NULL OR detected_at <= resolved_at",
            name="ck_security_violations_resolved_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_security_violations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_sec_violations_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_security_violations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_security_violations_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_security_violations_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_security_violations_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_security_violations_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_security_violations_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_security_violations_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_security_violations_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_security_violations"),
        sa.UniqueConstraint(
            "tenant_id",
            "violation_reference",
            name="uq_security_violations_tenant_id_violation_reference",
        ),
    )
    op.create_index(
        "ix_security_violations_tenant_id", "security_violations", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_security_violations_security_policy_id",
        "security_violations",
        ["security_policy_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_policy_rule_id",
        "security_violations",
        ["policy_rule_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_policy_evaluation_id",
        "security_violations",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_agent_id", "security_violations", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_security_violations_merchant_id", "security_violations", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_security_violations_product_id", "security_violations", ["product_id"], unique=False
    )
    op.create_index(
        "ix_security_violations_offer_id", "security_violations", ["offer_id"], unique=False
    )
    op.create_index(
        "ix_security_violations_purchase_intent_id",
        "security_violations",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_purchase_plan_id",
        "security_violations",
        ["purchase_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_commerce_transaction_id",
        "security_violations",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_violation_reference",
        "security_violations",
        ["violation_reference"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_violation_code",
        "security_violations",
        ["violation_code"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_request_id", "security_violations", ["request_id"], unique=False
    )
    op.create_index(
        "ix_security_violations_status", "security_violations", ["status"], unique=False
    )
    op.create_index(
        "ix_security_violations_severity", "security_violations", ["severity"], unique=False
    )
    op.create_index(
        "ix_security_violations_violation_type",
        "security_violations",
        ["violation_type"],
        unique=False,
    )
    op.create_index(
        "ix_security_violations_detected_at", "security_violations", ["detected_at"], unique=False
    )

    # 2. Create risk_signals table
    op.create_table(
        "risk_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("security_violation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("signal_reference", sa.String(length=100), nullable=False),
        sa.Column("signal_code", sa.String(length=100), nullable=False),
        sa.Column("signal_type", sa.String(length=50), nullable=False),
        sa.Column("signal_source", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="low"),
        sa.Column("risk_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("signal_value", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column(
            "signal_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "evidence_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "metadata_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_reference", sa.String(length=100), nullable=True),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
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
            "signal_type IN ('velocity', 'amount', 'frequency', 'authentication', "
            "'authorization', 'behaviour', 'fraud', 'device', 'identity', "
            "'agent_trust', 'merchant', 'product', 'inventory', 'transaction', "
            "'policy', 'compliance', 'geography', 'anomaly', 'spending', 'custom')",
            name="ck_risk_signals_signal_type",
        ),
        sa.CheckConstraint(
            "signal_source IN ('policy_engine', 'rule_engine', 'risk_engine', "
            "'fraud_engine', 'behaviour_engine', 'authentication', 'authorization', "
            "'agent_runtime', 'system', 'manual')",
            name="ck_risk_signals_signal_source",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'expired', 'suppressed', 'resolved')",
            name="ck_risk_signals_status",
        ),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_risk_signals_severity",
        ),
        sa.CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="ck_risk_signals_risk_score_bounds",
        ),
        sa.CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="ck_risk_signals_confidence_score_bounds",
        ),
        sa.CheckConstraint(
            "expires_at IS NULL OR observed_at <= expires_at",
            name="ck_risk_signals_date_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_risk_signals_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_risk_signals_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_risk_signals_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_risk_signals_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_risk_signals_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_risk_signals_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_risk_signals_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_risk_signals_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_risk_signals_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_risk_signals_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_violation_id"],
            ["security_violations.id"],
            name="fk_risk_signals_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_risk_signals"),
        sa.UniqueConstraint(
            "tenant_id",
            "signal_reference",
            name="uq_risk_signals_tenant_id_signal_reference",
        ),
    )
    op.create_index("ix_risk_signals_tenant_id", "risk_signals", ["tenant_id"], unique=False)
    op.create_index(
        "ix_risk_signals_security_policy_id", "risk_signals", ["security_policy_id"], unique=False
    )
    op.create_index(
        "ix_risk_signals_policy_rule_id", "risk_signals", ["policy_rule_id"], unique=False
    )
    op.create_index(
        "ix_risk_signals_policy_evaluation_id",
        "risk_signals",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_risk_signals_security_violation_id",
        "risk_signals",
        ["security_violation_id"],
        unique=False,
    )
    op.create_index("ix_risk_signals_agent_id", "risk_signals", ["agent_id"], unique=False)
    op.create_index("ix_risk_signals_merchant_id", "risk_signals", ["merchant_id"], unique=False)
    op.create_index("ix_risk_signals_product_id", "risk_signals", ["product_id"], unique=False)
    op.create_index("ix_risk_signals_offer_id", "risk_signals", ["offer_id"], unique=False)
    op.create_index(
        "ix_risk_signals_purchase_intent_id", "risk_signals", ["purchase_intent_id"], unique=False
    )
    op.create_index(
        "ix_risk_signals_purchase_plan_id", "risk_signals", ["purchase_plan_id"], unique=False
    )
    op.create_index(
        "ix_risk_signals_commerce_transaction_id",
        "risk_signals",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index("ix_risk_signals_signal_code", "risk_signals", ["signal_code"], unique=False)
    op.create_index("ix_risk_signals_request_id", "risk_signals", ["request_id"], unique=False)
    op.create_index(
        "ix_risk_signals_source_reference", "risk_signals", ["source_reference"], unique=False
    )
    op.create_index("ix_risk_signals_status", "risk_signals", ["status"], unique=False)
    op.create_index("ix_risk_signals_severity", "risk_signals", ["severity"], unique=False)
    op.create_index("ix_risk_signals_signal_type", "risk_signals", ["signal_type"], unique=False)
    op.create_index("ix_risk_signals_observed_at", "risk_signals", ["observed_at"], unique=False)


def downgrade() -> None:
    # 1. Drop risk_signals table
    op.drop_index("ix_risk_signals_observed_at", table_name="risk_signals")
    op.drop_index("ix_risk_signals_signal_type", table_name="risk_signals")
    op.drop_index("ix_risk_signals_severity", table_name="risk_signals")
    op.drop_index("ix_risk_signals_status", table_name="risk_signals")
    op.drop_index("ix_risk_signals_source_reference", table_name="risk_signals")
    op.drop_index("ix_risk_signals_request_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_signal_code", table_name="risk_signals")
    op.drop_index("ix_risk_signals_commerce_transaction_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_purchase_plan_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_purchase_intent_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_offer_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_product_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_merchant_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_agent_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_security_violation_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_policy_evaluation_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_policy_rule_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_security_policy_id", table_name="risk_signals")
    op.drop_index("ix_risk_signals_tenant_id", table_name="risk_signals")
    op.drop_table("risk_signals")

    # 2. Drop security_violations table
    op.drop_index("ix_security_violations_detected_at", table_name="security_violations")
    op.drop_index("ix_security_violations_violation_type", table_name="security_violations")
    op.drop_index("ix_security_violations_severity", table_name="security_violations")
    op.drop_index("ix_security_violations_status", table_name="security_violations")
    op.drop_index("ix_security_violations_request_id", table_name="security_violations")
    op.drop_index("ix_security_violations_violation_code", table_name="security_violations")
    op.drop_index("ix_security_violations_violation_reference", table_name="security_violations")
    op.drop_index(
        "ix_security_violations_commerce_transaction_id", table_name="security_violations"
    )
    op.drop_index("ix_security_violations_purchase_plan_id", table_name="security_violations")
    op.drop_index("ix_security_violations_purchase_intent_id", table_name="security_violations")
    op.drop_index("ix_security_violations_offer_id", table_name="security_violations")
    op.drop_index("ix_security_violations_product_id", table_name="security_violations")
    op.drop_index("ix_security_violations_merchant_id", table_name="security_violations")
    op.drop_index("ix_security_violations_agent_id", table_name="security_violations")
    op.drop_index("ix_security_violations_policy_evaluation_id", table_name="security_violations")
    op.drop_index("ix_security_violations_policy_rule_id", table_name="security_violations")
    op.drop_index("ix_security_violations_security_policy_id", table_name="security_violations")
    op.drop_index("ix_security_violations_tenant_id", table_name="security_violations")
    op.drop_table("security_violations")
