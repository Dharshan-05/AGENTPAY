"""Unit Tests for Phase 071 Reviewer Activity Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.reviewer_activity import ReviewerActivity


def test_01_reviewer_activity_table_exists() -> None:
    """1. Verify reviewer_activity table exists in Base.metadata."""
    assert "reviewer_activity" in Base.metadata.tables
    assert ReviewerActivity.__tablename__ == "reviewer_activity"


def test_02_reviewer_activity_exact_columns() -> None:
    """2. Verify exact columns exist on reviewer_activity."""
    table = Base.metadata.tables["reviewer_activity"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "reviewer_id",
        "review_queue_id",
        "approval_request_id",
        "approval_decision_id",
        "activity_reference",
        "activity_type",
        "activity_action",
        "actor_type",
        "actor_id",
        "request_id",
        "activity_payload",
        "occurred_at",
        "created_at",
    }
    assert expected.issubset(column_names)


def test_03_reviewer_activity_pk() -> None:
    """3. Verify primary key pk_reviewer_activity."""
    table = Base.metadata.tables["reviewer_activity"]
    assert table.primary_key.name == "pk_reviewer_activity"


def test_04_reviewer_activity_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["reviewer_activity"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_reviewer_activity_tenant_id" in ix_names


def test_05_reviewer_activity_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["reviewer_activity"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_reviewer_activity_reviewer_id_users" in fk_dict
    assert "fk_reviewer_activity_review_queue_id_review_queue" in fk_dict
    assert "fk_reviewer_activity_approval_request_id_approval_requests" in fk_dict
    assert "fk_reviewer_activity_approval_decision_id_approval_decisions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_reviewer_activity_reviewer_id" in ix_names
    assert "ix_reviewer_activity_review_queue_id" in ix_names
    assert "ix_reviewer_activity_approval_request_id" in ix_names
    assert "ix_reviewer_activity_approval_decision_id" in ix_names
    assert "ix_reviewer_activity_activity_reference" in ix_names
    assert "ix_reviewer_activity_activity_type" in ix_names
    assert "ix_reviewer_activity_activity_action" in ix_names
    assert "ix_reviewer_activity_request_id" in ix_names
    assert "ix_reviewer_activity_actor_id" in ix_names
    assert "ix_reviewer_activity_occurred_at" in ix_names


def test_06_reviewer_activity_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped activity_reference uniqueness constraint exists."""
    table = Base.metadata.tables["reviewer_activity"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_reviewer_activity_tenant_id_activity_reference" in uq_names


def test_07_reviewer_activity_enum_constraints() -> None:
    """7. Verify activity_type and activity_action check constraints exist."""
    table = Base.metadata.tables["reviewer_activity"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_reviewer_activity_activity_type" in ck_names
    assert "ck_reviewer_activity_activity_action" in ck_names


def test_08_reviewer_activity_append_only_structure() -> None:
    """8. Verify reviewer_activity is APPEND-ONLY and lacks updated_at/deleted_at."""
    table = Base.metadata.tables["reviewer_activity"]
    column_names = {c.name for c in table.columns}
    assert "updated_at" not in column_names
    assert "deleted_at" not in column_names
    assert "occurred_at" in column_names
    assert "created_at" in column_names


def test_09_reviewer_activity_jsonb_payload() -> None:
    """9. Verify activity_payload uses JSONB."""
    table = Base.metadata.tables["reviewer_activity"]
    col = table.columns["activity_payload"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_reviewer_activity_repr_redaction() -> None:
    """10. Verify ReviewerActivity.__repr__ does NOT leak activity_payload."""
    ra = ReviewerActivity(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        reviewer_id=uuid.uuid4(),
        activity_reference="ACT-001",
        activity_type="review",
        activity_action="viewed",
        activity_payload={"secret_key": "hidden"},
    )
    repr_str = repr(ra)
    assert "action='viewed'" in repr_str
    assert "secret_key" not in repr_str


def test_11_reviewer_activity_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on reviewer_activity."""
    columns = {c.name for c in Base.metadata.tables["reviewer_activity"].columns}
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


def test_12_reviewer_activity_tenant_isolation() -> None:
    """12. Verify tenant isolation on ReviewerActivity."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    ra = ReviewerActivity(
        id=uuid.uuid4(),
        tenant_id=t1,
        reviewer_id=uuid.uuid4(),
        activity_reference="ACT-T1",
        activity_action="claimed",
    )
    assert ra.tenant_id == t1
    assert (ra.tenant_id == t2) is False


def test_13_reviewer_activity_relationships() -> None:
    """13. Verify ReviewerActivity relationships."""
    assert hasattr(ReviewerActivity, "reviewer")
    assert hasattr(ReviewerActivity, "review_queue")
    assert hasattr(ReviewerActivity, "approval_request")
    assert hasattr(ReviewerActivity, "approval_decision")
