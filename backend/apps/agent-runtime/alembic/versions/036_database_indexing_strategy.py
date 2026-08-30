"""database_indexing_strategy

Revision ID: 036_database_indexing_strategy
Revises: 035_risk_decision_audits
Create Date: 2026-08-26 08:43:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "036_database_indexing_strategy"
down_revision: str | None = "035_risk_decision_audits"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Missing FK Index Coverage on refresh_tokens
    op.create_index(
        "ix_refresh_tokens_parent_token_id", "refresh_tokens", ["parent_token_id"], unique=False
    )

    # 2. Tenant Composite Operational & Filtering Indexes
    op.create_index(
        "ix_payment_orders_tenant_status", "payment_orders", ["tenant_id", "status"], unique=False
    )
    op.create_index(
        "ix_payment_transactions_tenant_status",
        "payment_transactions",
        ["tenant_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_review_queue_tenant_status_priority",
        "review_queue",
        ["tenant_id", "status", "priority"],
        unique=False,
    )
    op.create_index(
        "ix_approval_requests_tenant_status",
        "approval_requests",
        ["tenant_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_audit_logs_tenant_occurred_at", "audit_logs", ["tenant_id", "occurred_at"], unique=False
    )
    op.create_index(
        "ix_security_events_tenant_occurred_at",
        "security_events",
        ["tenant_id", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "ix_risk_decision_audits_tenant_occurred_at",
        "risk_decision_audits",
        ["tenant_id", "occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_risk_decision_audits_tenant_occurred_at", table_name="risk_decision_audits")
    op.drop_index("ix_security_events_tenant_occurred_at", table_name="security_events")
    op.drop_index("ix_audit_logs_tenant_occurred_at", table_name="audit_logs")
    op.drop_index("ix_approval_requests_tenant_status", table_name="approval_requests")
    op.drop_index("ix_review_queue_tenant_status_priority", table_name="review_queue")
    op.drop_index("ix_payment_transactions_tenant_status", table_name="payment_transactions")
    op.drop_index("ix_payment_orders_tenant_status", table_name="payment_orders")
    op.drop_index("ix_refresh_tokens_parent_token_id", table_name="refresh_tokens")
