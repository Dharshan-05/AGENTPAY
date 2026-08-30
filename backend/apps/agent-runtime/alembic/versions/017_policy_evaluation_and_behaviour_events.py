"""policy_evaluation_and_behaviour_events

Revision ID: 017_policy_evaluation_and_behaviour_events
Revises: 016_security_policies_and_policy_rules
Create Date: 2026-08-25 23:32:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017_policy_evaluation_and_behaviour_events"
down_revision: str | None = "016_security_policies_and_policy_rules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create policy_evaluations table
    op.create_table(
        "policy_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_rule_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("evaluation_reference", sa.String(length=100), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("evaluation_type", sa.String(length=50), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="completed"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("evaluation_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "condition_result",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "evaluation_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("failure_code", sa.String(length=100), nullable=True),
        sa.Column("failure_message", sa.String(length=500), nullable=True),
        sa.Column(
            "evaluated_at",
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
            "evaluation_type IN ('authorization', 'transaction', 'fraud', 'risk', "
            "'compliance', 'spending', 'access', 'agent', 'commerce')",
            name="ck_policy_evaluations_evaluation_type",
        ),
        sa.CheckConstraint(
            "decision IN ('allow', 'deny', 'challenge', 'review', 'alert', "
            "'block', 'require_approval')",
            name="ck_policy_evaluations_decision",
        ),
        sa.CheckConstraint(
            "result IN ('success', 'failure', 'error', 'skipped')",
            name="ck_policy_evaluations_result",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'expired', 'cancelled')",
            name="ck_policy_evaluations_status",
        ),
        sa.CheckConstraint("priority >= 0", name="ck_policy_evaluations_priority_nonnegative"),
        sa.CheckConstraint("evaluation_version > 0", name="ck_policy_evaluations_version_positive"),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_policy_evaluations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_policy_eval_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_policy_evaluations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_policy_evaluations_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name="fk_policy_evaluations_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_policy_evaluations_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_policy_evaluations_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_policy_evaluations_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_policy_evaluations_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_policy_evaluations"),
        sa.UniqueConstraint(
            "tenant_id",
            "evaluation_reference",
            name="uq_policy_evaluations_tenant_id_evaluation_reference",
        ),
    )
    op.create_index(
        "ix_policy_evaluations_tenant_id", "policy_evaluations", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_policy_evaluations_security_policy_id",
        "policy_evaluations",
        ["security_policy_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_evaluations_policy_rule_id",
        "policy_evaluations",
        ["policy_rule_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_evaluations_merchant_id", "policy_evaluations", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_policy_evaluations_agent_id", "policy_evaluations", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_policy_evaluations_product_id", "policy_evaluations", ["product_id"], unique=False
    )
    op.create_index(
        "ix_policy_evaluations_offer_id", "policy_evaluations", ["offer_id"], unique=False
    )
    op.create_index(
        "ix_policy_evaluations_purchase_intent_id",
        "policy_evaluations",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_evaluations_purchase_plan_id",
        "policy_evaluations",
        ["purchase_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_evaluations_commerce_transaction_id",
        "policy_evaluations",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_policy_evaluations_evaluation_type",
        "policy_evaluations",
        ["evaluation_type"],
        unique=False,
    )
    op.create_index(
        "ix_policy_evaluations_decision", "policy_evaluations", ["decision"], unique=False
    )
    op.create_index("ix_policy_evaluations_status", "policy_evaluations", ["status"], unique=False)
    op.create_index(
        "ix_policy_evaluations_evaluated_at", "policy_evaluations", ["evaluated_at"], unique=False
    )
    op.create_index(
        "ix_policy_evaluations_request_id", "policy_evaluations", ["request_id"], unique=False
    )

    # 2. Create behaviour_events table
    op.create_table(
        "behaviour_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_reference", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_action", sa.String(length=50), nullable=False),
        sa.Column("event_result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_evaluation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sequence_number", sa.BigInteger(), nullable=False),
        sa.Column(
            "event_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
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
            "event_type IN ('agent', 'authentication', 'authorization', 'policy', "
            "'commerce', 'purchase', 'inventory', 'merchant', 'product', "
            "'offer', 'transaction', 'system')",
            name="ck_behaviour_events_event_type",
        ),
        sa.CheckConstraint(
            "event_action IN ('created', 'requested', 'approved', 'rejected', "
            "'executed', 'completed', 'failed', 'cancelled', 'viewed', "
            "'selected', 'initiated', 'updated', 'deleted', 'evaluated')",
            name="ck_behaviour_events_event_action",
        ),
        sa.CheckConstraint(
            "event_result IN ('success', 'failure', 'pending', 'skipped')",
            name="ck_behaviour_events_event_result",
        ),
        sa.CheckConstraint("sequence_number >= 0", name="ck_behaviour_events_sequence_nonnegative"),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_behaviour_events_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_behaviour_events_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_behaviour_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_behaviour_events_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_evaluation_id"],
            ["policy_evaluations.id"],
            name="fk_behaviour_events_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_behaviour_events_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_behaviour_events_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_behaviour_events_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_behaviour_events"),
        sa.UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_behaviour_events_tenant_id_event_reference",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "sequence_number",
            name="uq_behaviour_events_tenant_id_sequence_number",
        ),
    )
    op.create_index(
        "ix_behaviour_events_tenant_id", "behaviour_events", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_behaviour_events_event_type", "behaviour_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_behaviour_events_event_action", "behaviour_events", ["event_action"], unique=False
    )
    op.create_index(
        "ix_behaviour_events_event_result", "behaviour_events", ["event_result"], unique=False
    )
    op.create_index("ix_behaviour_events_agent_id", "behaviour_events", ["agent_id"], unique=False)
    op.create_index(
        "ix_behaviour_events_merchant_id", "behaviour_events", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_behaviour_events_product_id", "behaviour_events", ["product_id"], unique=False
    )
    op.create_index("ix_behaviour_events_offer_id", "behaviour_events", ["offer_id"], unique=False)
    op.create_index(
        "ix_behaviour_events_purchase_intent_id",
        "behaviour_events",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_behaviour_events_purchase_plan_id",
        "behaviour_events",
        ["purchase_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_behaviour_events_commerce_transaction_id",
        "behaviour_events",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_behaviour_events_policy_evaluation_id",
        "behaviour_events",
        ["policy_evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_behaviour_events_request_id", "behaviour_events", ["request_id"], unique=False
    )
    op.create_index(
        "ix_behaviour_events_occurred_at", "behaviour_events", ["occurred_at"], unique=False
    )


def downgrade() -> None:
    # 1. Drop behaviour_events table
    op.drop_index("ix_behaviour_events_occurred_at", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_request_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_policy_evaluation_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_commerce_transaction_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_purchase_plan_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_purchase_intent_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_offer_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_product_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_merchant_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_agent_id", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_event_result", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_event_action", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_event_type", table_name="behaviour_events")
    op.drop_index("ix_behaviour_events_tenant_id", table_name="behaviour_events")
    op.drop_table("behaviour_events")

    # 2. Drop policy_evaluations table
    op.drop_index("ix_policy_evaluations_request_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_evaluated_at", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_status", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_decision", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_evaluation_type", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_commerce_transaction_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_purchase_plan_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_purchase_intent_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_offer_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_product_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_agent_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_merchant_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_policy_rule_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_security_policy_id", table_name="policy_evaluations")
    op.drop_index("ix_policy_evaluations_tenant_id", table_name="policy_evaluations")
    op.drop_table("policy_evaluations")
