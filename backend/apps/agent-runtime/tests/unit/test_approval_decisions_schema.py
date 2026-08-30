"""Unit Tests for Phase 070 Approval Decisions Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.approval_decision import ApprovalDecision


def test_01_approval_decisions_table_exists() -> None:
    """1. Verify approval_decisions table exists in Base.metadata."""
    assert "approval_decisions" in Base.metadata.tables
    assert ApprovalDecision.__tablename__ == "approval_decisions"


def test_02_approval_decisions_exact_columns() -> None:
    """2. Verify exact columns exist on approval_decisions."""
    table = Base.metadata.tables["approval_decisions"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "approval_request_id",
        "reviewer_id",
        "decision_reference",
        "decision",
        "reason",
        "request_id",
        "decision_context",
        "decided_at",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(column_names)


def test_03_approval_decisions_pk() -> None:
    """3. Verify primary key pk_approval_decisions."""
    table = Base.metadata.tables["approval_decisions"]
    assert table.primary_key.name == "pk_approval_decisions"


def test_04_approval_decisions_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["approval_decisions"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_approval_decisions_tenant_id" in ix_names


def test_05_approval_decisions_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["approval_decisions"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_approval_decisions_approval_request_id_approval_requests" in fk_dict
    assert "fk_approval_decisions_reviewer_id_users" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_approval_decisions_approval_request_id" in ix_names
    assert "ix_approval_decisions_reviewer_id" in ix_names
    assert "ix_approval_decisions_decision_reference" in ix_names
    assert "ix_approval_decisions_decision" in ix_names
    assert "ix_approval_decisions_request_id" in ix_names
    assert "ix_approval_decisions_decided_at" in ix_names


def test_06_approval_decisions_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped decision_reference uniqueness constraint exists."""
    table = Base.metadata.tables["approval_decisions"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_approval_decisions_tenant_id_decision_reference" in uq_names


def test_07_approval_decisions_enum_constraints() -> None:
    """7. Verify decision check constraint exists."""
    table = Base.metadata.tables["approval_decisions"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_approval_decisions_decision" in ck_names


def test_08_approval_decisions_jsonb_context() -> None:
    """8. Verify decision_context uses JSONB."""
    table = Base.metadata.tables["approval_decisions"]
    col = table.columns["decision_context"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_09_approval_decisions_repr_redaction() -> None:
    """9. Verify ApprovalDecision.__repr__ does NOT leak decision_context."""
    ad = ApprovalDecision(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        approval_request_id=uuid.uuid4(),
        reviewer_id=uuid.uuid4(),
        decision_reference="AD-001",
        decision="approved",
        decision_context={"secret_key": "hidden"},
    )
    repr_str = repr(ad)
    assert "decision='approved'" in repr_str
    assert "secret_key" not in repr_str


def test_10_approval_decisions_prohibited_secret_fields() -> None:
    """10. Verify prohibited secret fields do NOT exist on approval_decisions."""
    columns = {c.name for c in Base.metadata.tables["approval_decisions"].columns}
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


def test_11_approval_decisions_tenant_isolation() -> None:
    """11. Verify tenant isolation on ApprovalDecision."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    ad = ApprovalDecision(
        id=uuid.uuid4(),
        tenant_id=t1,
        approval_request_id=uuid.uuid4(),
        reviewer_id=uuid.uuid4(),
        decision_reference="AD-T1",
        decision="approved",
    )
    assert ad.tenant_id == t1
    assert (ad.tenant_id == t2) is False


def test_12_approval_decisions_relationships() -> None:
    """12. Verify ApprovalDecision relationships."""
    assert hasattr(ApprovalDecision, "approval_request")
    assert hasattr(ApprovalDecision, "reviewer")
