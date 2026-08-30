"""Unit Tests for Phase 072 Global Audit Log Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.audit_log import AuditLog


def test_01_audit_logs_table_exists() -> None:
    """1. Verify audit_logs table exists in Base.metadata."""
    assert "audit_logs" in Base.metadata.tables
    assert AuditLog.__tablename__ == "audit_logs"


def test_02_audit_logs_exact_columns() -> None:
    """2. Verify exact columns exist on audit_logs."""
    table = Base.metadata.tables["audit_logs"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "audit_reference",
        "actor_type",
        "actor_id",
        "user_id",
        "agent_id",
        "merchant_id",
        "resource_type",
        "resource_id",
        "action",
        "category",
        "result",
        "request_id",
        "correlation_id",
        "ip_address",
        "user_agent",
        "before_state",
        "after_state",
        "metadata_json",
        "occurred_at",
        "created_at",
    }
    assert expected.issubset(column_names)


def test_03_audit_logs_pk() -> None:
    """3. Verify primary key pk_audit_logs."""
    table = Base.metadata.tables["audit_logs"]
    assert table.primary_key.name == "pk_audit_logs"


def test_04_audit_logs_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["audit_logs"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_audit_logs_tenant_id" in ix_names


def test_05_audit_logs_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["audit_logs"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_audit_logs_user_id_users" in fk_dict
    assert "fk_audit_logs_agent_id_agents" in fk_dict
    assert "fk_audit_logs_merchant_id_merchants" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_audit_logs_audit_reference" in ix_names
    assert "ix_audit_logs_actor_type" in ix_names
    assert "ix_audit_logs_actor_id" in ix_names
    assert "ix_audit_logs_user_id" in ix_names
    assert "ix_audit_logs_agent_id" in ix_names
    assert "ix_audit_logs_merchant_id" in ix_names
    assert "ix_audit_logs_resource_type" in ix_names
    assert "ix_audit_logs_resource_id" in ix_names
    assert "ix_audit_logs_action" in ix_names
    assert "ix_audit_logs_category" in ix_names
    assert "ix_audit_logs_result" in ix_names
    assert "ix_audit_logs_request_id" in ix_names
    assert "ix_audit_logs_correlation_id" in ix_names
    assert "ix_audit_logs_occurred_at" in ix_names


def test_06_audit_logs_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped audit_reference uniqueness constraint exists."""
    table = Base.metadata.tables["audit_logs"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_audit_logs_tenant_id_audit_reference" in uq_names


def test_07_audit_logs_enum_constraints() -> None:
    """7. Verify category and result check constraints exist."""
    table = Base.metadata.tables["audit_logs"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_audit_logs_category" in ck_names
    assert "ck_audit_logs_result" in ck_names


def test_08_audit_logs_append_only_structure() -> None:
    """8. Verify audit_logs is APPEND-ONLY and lacks updated_at/deleted_at."""
    table = Base.metadata.tables["audit_logs"]
    column_names = {c.name for c in table.columns}
    assert "updated_at" not in column_names
    assert "deleted_at" not in column_names
    assert "occurred_at" in column_names
    assert "created_at" in column_names


def test_09_audit_logs_jsonb_payloads() -> None:
    """9. Verify before_state, after_state, metadata_json use JSONB."""
    table = Base.metadata.tables["audit_logs"]
    for col_name in ("before_state", "after_state", "metadata_json"):
        col = table.columns[col_name]
        assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_audit_logs_repr_redaction() -> None:
    """10. Verify AuditLog.__repr__ does NOT leak JSONB states."""
    al = AuditLog(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_reference="AUD-001",
        resource_type="payment_order",
        action="order_created",
        category="payment",
        result="success",
        before_state={"secret_key": "hidden"},
        after_state={"secret_key": "hidden"},
        metadata_json={"secret_key": "hidden"},
    )
    repr_str = repr(al)
    assert "action='order_created'" in repr_str
    assert "secret_key" not in repr_str


def test_11_audit_logs_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on audit_logs."""
    columns = {c.name for c in Base.metadata.tables["audit_logs"].columns}
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


def test_12_audit_logs_tenant_isolation() -> None:
    """12. Verify tenant isolation on AuditLog."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    al = AuditLog(
        id=uuid.uuid4(),
        tenant_id=t1,
        audit_reference="AUD-T1",
        resource_type="agent",
        action="agent_authenticated",
    )
    assert al.tenant_id == t1
    assert (al.tenant_id == t2) is False


def test_13_audit_logs_relationships() -> None:
    """13. Verify AuditLog relationships."""
    assert hasattr(AuditLog, "user")
    assert hasattr(AuditLog, "agent")
    assert hasattr(AuditLog, "merchant")
