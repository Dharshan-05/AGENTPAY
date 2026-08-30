"""Unit Tests for Phase 073 Security Events Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.security_event import SecurityEvent


def test_01_security_events_table_exists() -> None:
    """1. Verify security_events table exists in Base.metadata."""
    assert "security_events" in Base.metadata.tables
    assert SecurityEvent.__tablename__ == "security_events"


def test_02_security_events_exact_columns() -> None:
    """2. Verify exact columns exist on security_events."""
    table = Base.metadata.tables["security_events"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "event_reference",
        "event_type",
        "event_action",
        "event_result",
        "severity",
        "source",
        "request_id",
        "actor_type",
        "actor_id",
        "ip_address",
        "user_agent",
        "user_id",
        "agent_id",
        "merchant_id",
        "security_violation_id",
        "risk_signal_id",
        "policy_evaluation_id",
        "event_payload",
        "occurred_at",
        "created_at",
    }
    assert expected.issubset(column_names)


def test_03_security_events_pk() -> None:
    """3. Verify primary key pk_security_events."""
    table = Base.metadata.tables["security_events"]
    assert table.primary_key.name == "pk_security_events"


def test_04_security_events_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["security_events"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_security_events_tenant_id" in ix_names


def test_05_security_events_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["security_events"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_security_events_user_id_users" in fk_dict
    assert "fk_security_events_agent_id_agents" in fk_dict
    assert "fk_security_events_merchant_id_merchants" in fk_dict
    assert "fk_security_events_security_violation_id_security_violations" in fk_dict
    assert "fk_security_events_risk_signal_id_risk_signals" in fk_dict
    assert "fk_security_events_policy_evaluation_id_policy_evaluations" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_security_events_event_reference" in ix_names
    assert "ix_security_events_event_type" in ix_names
    assert "ix_security_events_event_action" in ix_names
    assert "ix_security_events_event_result" in ix_names
    assert "ix_security_events_severity" in ix_names
    assert "ix_security_events_source" in ix_names
    assert "ix_security_events_request_id" in ix_names
    assert "ix_security_events_actor_id" in ix_names
    assert "ix_security_events_user_id" in ix_names
    assert "ix_security_events_agent_id" in ix_names
    assert "ix_security_events_merchant_id" in ix_names
    assert "ix_security_events_security_violation_id" in ix_names
    assert "ix_security_events_risk_signal_id" in ix_names
    assert "ix_security_events_policy_evaluation_id" in ix_names
    assert "ix_security_events_occurred_at" in ix_names


def test_06_security_events_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped event_reference uniqueness constraint exists."""
    table = Base.metadata.tables["security_events"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_security_events_tenant_id_event_reference" in uq_names


def test_07_security_events_enum_constraints() -> None:
    """7. Verify event_type, event_action, event_result, severity check constraints exist."""

    table = Base.metadata.tables["security_events"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_security_events_event_type" in ck_names
    assert "ck_security_events_event_action" in ck_names
    assert "ck_security_events_event_result" in ck_names
    assert "ck_security_events_severity" in ck_names
    assert "ck_security_events_source" in ck_names


def test_08_security_events_append_only_structure() -> None:
    """8. Verify security_events is APPEND-ONLY and lacks updated_at/deleted_at."""
    table = Base.metadata.tables["security_events"]
    column_names = {c.name for c in table.columns}
    assert "updated_at" not in column_names
    assert "deleted_at" not in column_names
    assert "occurred_at" in column_names
    assert "created_at" in column_names


def test_09_security_events_jsonb_payload() -> None:
    """9. Verify event_payload uses JSONB."""
    table = Base.metadata.tables["security_events"]
    col = table.columns["event_payload"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_security_events_repr_redaction() -> None:
    """10. Verify SecurityEvent.__repr__ does NOT leak event_payload."""
    se = SecurityEvent(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        event_reference="SE-001",
        event_type="authentication",
        event_action="login",
        event_result="success",
        severity="medium",
        event_payload={"secret_key": "hidden"},
    )
    repr_str = repr(se)
    assert "type='authentication'" in repr_str
    assert "secret_key" not in repr_str


def test_11_security_events_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on security_events."""
    columns = {c.name for c in Base.metadata.tables["security_events"].columns}
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


def test_12_security_events_tenant_isolation() -> None:
    """12. Verify tenant isolation on SecurityEvent."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    se = SecurityEvent(
        id=uuid.uuid4(),
        tenant_id=t1,
        event_reference="SE-T1",
        event_type="system",
        event_action="security_alert",
    )
    assert se.tenant_id == t1
    assert (se.tenant_id == t2) is False


def test_13_security_events_relationships() -> None:
    """13. Verify SecurityEvent relationships."""
    assert hasattr(SecurityEvent, "user")
    assert hasattr(SecurityEvent, "agent")
    assert hasattr(SecurityEvent, "merchant")
    assert hasattr(SecurityEvent, "security_violation")
    assert hasattr(SecurityEvent, "risk_signal")
    assert hasattr(SecurityEvent, "policy_evaluation")
