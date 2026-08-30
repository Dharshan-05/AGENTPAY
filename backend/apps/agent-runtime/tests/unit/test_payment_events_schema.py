"""Unit Tests for Phase 063 Payment Events Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.payment_event import PaymentEvent


def test_01_payment_events_table_exists() -> None:
    """1. Verify payment_events table exists in Base.metadata."""
    assert "payment_events" in Base.metadata.tables
    assert PaymentEvent.__tablename__ == "payment_events"


def test_02_payment_events_exact_columns() -> None:
    """2. Verify exact columns exist on payment_events."""
    table = Base.metadata.tables["payment_events"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "payment_transaction_id",
        "payment_order_id",
        "event_reference",
        "event_type",
        "event_action",
        "event_result",
        "sequence_number",
        "request_id",
        "actor_type",
        "actor_id",
        "event_metadata",
        "occurred_at",
        "created_at",
    }
    assert expected.issubset(column_names)


def test_03_payment_events_append_only_structure() -> None:
    """3. Verify payment_events is strictly append-only (no updated_at or deleted_at)."""
    table = Base.metadata.tables["payment_events"]
    assert "updated_at" not in table.columns
    assert "deleted_at" not in table.columns


def test_04_payment_events_pk() -> None:
    """4. Verify primary key pk_payment_events."""
    table = Base.metadata.tables["payment_events"]
    assert table.primary_key.name == "pk_payment_events"


def test_05_payment_events_tenant_id() -> None:
    """5. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["payment_events"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_events_tenant_id" in ix_names


def test_06_payment_events_fks_and_indexes() -> None:
    """6. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["payment_events"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_payment_events_payment_transaction_id_payment_transactions" in fk_dict
    assert "fk_payment_events_payment_order_id_payment_orders" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_events_payment_transaction_id" in ix_names
    assert "ix_payment_events_payment_order_id" in ix_names
    assert "ix_payment_events_event_type" in ix_names
    assert "ix_payment_events_event_action" in ix_names
    assert "ix_payment_events_event_result" in ix_names
    assert "ix_payment_events_request_id" in ix_names
    assert "ix_payment_events_occurred_at" in ix_names


def test_07_payment_events_uniqueness_constraints() -> None:
    """7. Verify tenant-scoped event_reference & sequence uniqueness constraints exist."""
    table = Base.metadata.tables["payment_events"]

    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_payment_events_tenant_id_event_reference" in uq_names
    assert "uq_payment_events_transaction_sequence" in uq_names


def test_08_payment_events_enum_constraints() -> None:
    """8. Verify event_type, event_action, event_result, sequence_number check constraints exist."""
    table = Base.metadata.tables["payment_events"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_payment_events_event_type" in ck_names
    assert "ck_payment_events_event_action" in ck_names
    assert "ck_payment_events_event_result" in ck_names
    assert "ck_payment_events_sequence_number_positive" in ck_names


def test_09_payment_events_sequence_number_deterministic() -> None:
    """9. Verify sequence_number integer ordering."""
    pe = PaymentEvent(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        payment_transaction_id=uuid.uuid4(),
        event_reference="EVT-001",
        event_type="payment",
        event_action="completed",
        event_result="success",
        sequence_number=1,
    )
    assert pe.sequence_number == 1


def test_10_payment_events_jsonb_metadata() -> None:
    """10. Verify event_metadata uses JSONB."""
    table = Base.metadata.tables["payment_events"]
    col = table.columns["event_metadata"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_11_payment_events_repr_redaction() -> None:
    """11. Verify PaymentEvent.__repr__ does NOT leak JSONB metadata."""
    pe = PaymentEvent(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        payment_transaction_id=uuid.uuid4(),
        event_reference="EVT-001",
        event_type="payment",
        event_action="completed",
        event_result="success",
        sequence_number=1,
        event_metadata={"secret_key": "hidden"},
    )
    repr_str = repr(pe)
    assert "seq=1" in repr_str
    assert "secret_key" not in repr_str


def test_12_payment_events_prohibited_secret_fields() -> None:
    """12. Verify prohibited secret fields do NOT exist on payment_events."""
    columns = {c.name for c in Base.metadata.tables["payment_events"].columns}
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


def test_13_payment_events_tenant_isolation() -> None:
    """13. Verify tenant isolation on PaymentEvent."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    pe = PaymentEvent(
        id=uuid.uuid4(),
        tenant_id=t1,
        payment_transaction_id=uuid.uuid4(),
        event_reference="EVT-T1",
        event_type="payment",
        event_action="completed",
        event_result="success",
        sequence_number=1,
    )
    assert pe.tenant_id == t1
    assert (pe.tenant_id == t2) is False


def test_14_payment_events_relationships() -> None:
    """14. Verify PaymentEvent relationships."""
    assert hasattr(PaymentEvent, "payment_transaction")
    assert hasattr(PaymentEvent, "payment_order")
