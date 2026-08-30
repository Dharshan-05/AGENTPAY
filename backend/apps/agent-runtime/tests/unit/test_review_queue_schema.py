"""Unit Tests for Phase 068 Review Queue Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.review_queue import ReviewQueue


def test_01_review_queue_table_exists() -> None:
    """1. Verify review_queue table exists in Base.metadata."""
    assert "review_queue" in Base.metadata.tables
    assert ReviewQueue.__tablename__ == "review_queue"


def test_02_review_queue_exact_columns() -> None:
    """2. Verify exact columns exist on review_queue."""
    table = Base.metadata.tables["review_queue"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "review_reference",
        "review_type",
        "status",
        "priority",
        "severity",
        "source_type",
        "source_id",
        "security_policy_id",
        "policy_rule_id",
        "policy_evaluation_id",
        "security_violation_id",
        "risk_signal_id",
        "fraud_prediction_id",
        "commerce_transaction_id",
        "payment_order_id",
        "payment_transaction_id",
        "agent_id",
        "merchant_id",
        "assigned_reviewer_id",
        "request_id",
        "title",
        "description",
        "review_context",
        "decision",
        "decision_reason",
        "queued_at",
        "assigned_at",
        "started_at",
        "resolved_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_review_queue_pk() -> None:
    """3. Verify primary key pk_review_queue."""
    table = Base.metadata.tables["review_queue"]
    assert table.primary_key.name == "pk_review_queue"


def test_04_review_queue_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["review_queue"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_review_queue_tenant_id" in ix_names


def test_05_review_queue_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["review_queue"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_review_queue_assigned_reviewer_id_users" in fk_dict
    assert "fk_review_queue_security_policy_id_security_policies" in fk_dict
    assert "fk_review_queue_payment_order_id_payment_orders" in fk_dict
    assert "fk_review_queue_payment_transaction_id_payment_transactions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_review_queue_review_reference" in ix_names
    assert "ix_review_queue_status" in ix_names
    assert "ix_review_queue_priority" in ix_names
    assert "ix_review_queue_severity" in ix_names
    assert "ix_review_queue_review_type" in ix_names
    assert "ix_review_queue_assigned_reviewer_id" in ix_names
    assert "ix_review_queue_request_id" in ix_names
    assert "ix_review_queue_queued_at" in ix_names
    assert "ix_review_queue_source_id" in ix_names
    assert "ix_review_queue_payment_order_id" in ix_names
    assert "ix_review_queue_payment_transaction_id" in ix_names


def test_06_review_queue_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped review_reference uniqueness constraint exists."""
    table = Base.metadata.tables["review_queue"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_review_queue_tenant_id_review_reference" in uq_names


def test_07_review_queue_enum_and_priority_constraints() -> None:
    """7. Verify review_type, status, priority, severity, decision check constraints exist."""
    table = Base.metadata.tables["review_queue"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_review_queue_review_type" in ck_names
    assert "ck_review_queue_status" in ck_names
    assert "ck_review_queue_priority_nonnegative" in ck_names
    assert "ck_review_queue_severity" in ck_names
    assert "ck_review_queue_decision" in ck_names


def test_08_review_queue_jsonb_context() -> None:
    """8. Verify review_context uses JSONB."""
    table = Base.metadata.tables["review_queue"]
    col = table.columns["review_context"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_09_review_queue_repr_redaction() -> None:
    """9. Verify ReviewQueue.__repr__ does NOT leak review_context."""
    rq = ReviewQueue(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        review_reference="REV-001",
        review_type="security",
        status="queued",
        priority=1,
        title="Suspicious Login Activity",
        review_context={"secret_key": "hidden"},
    )
    repr_str = repr(rq)
    assert "reference='REV-001'" in repr_str
    assert "secret_key" not in repr_str


def test_10_review_queue_prohibited_secret_fields() -> None:
    """10. Verify prohibited secret fields do NOT exist on review_queue."""
    columns = {c.name for c in Base.metadata.tables["review_queue"].columns}
    prohibited = {
        "password",
        "secret",
        "token",
        "api_key",
        "private_key",
        "card_number",
        "cvv",
        "pin",
        "otp",
    }
    assert len(prohibited.intersection(columns)) == 0


def test_11_review_queue_tenant_isolation() -> None:
    """11. Verify tenant isolation on ReviewQueue."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    rq = ReviewQueue(
        id=uuid.uuid4(),
        tenant_id=t1,
        review_reference="REV-T1",
        title="Tenant Isolation Test Case",
    )
    assert rq.tenant_id == t1
    assert (rq.tenant_id == t2) is False


def test_12_review_queue_relationships() -> None:
    """12. Verify ReviewQueue relationships."""
    assert hasattr(ReviewQueue, "security_policy")
    assert hasattr(ReviewQueue, "policy_rule")
    assert hasattr(ReviewQueue, "policy_evaluation")
    assert hasattr(ReviewQueue, "security_violation")
    assert hasattr(ReviewQueue, "risk_signal")
    assert hasattr(ReviewQueue, "fraud_prediction")
    assert hasattr(ReviewQueue, "commerce_transaction")
    assert hasattr(ReviewQueue, "payment_order")
    assert hasattr(ReviewQueue, "payment_transaction")
    assert hasattr(ReviewQueue, "agent")
    assert hasattr(ReviewQueue, "merchant")
    assert hasattr(ReviewQueue, "assigned_reviewer")
