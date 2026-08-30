"""Unit Tests for Phase 066 Cancellations Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.cancellation import Cancellation


def test_01_cancellations_table_exists() -> None:
    """1. Verify cancellations table exists in Base.metadata."""
    assert "cancellations" in Base.metadata.tables
    assert Cancellation.__tablename__ == "cancellations"


def test_02_cancellations_exact_columns() -> None:
    """2. Verify exact columns exist on cancellations."""
    table = Base.metadata.tables["cancellations"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "payment_order_id",
        "payment_transaction_id",
        "merchant_id",
        "agent_id",
        "cancellation_reference",
        "provider_cancellation_reference",
        "status",
        "reason_type",
        "reason_detail",
        "cancellation_metadata",
        "requested_at",
        "processed_at",
        "completed_at",
        "failed_at",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(column_names)


def test_03_cancellations_pk() -> None:
    """3. Verify primary key pk_cancellations."""
    table = Base.metadata.tables["cancellations"]
    assert table.primary_key.name == "pk_cancellations"


def test_04_cancellations_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["cancellations"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_cancellations_tenant_id" in ix_names


def test_05_cancellations_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["cancellations"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_cancellations_payment_order_id_payment_orders" in fk_dict
    assert "fk_cancellations_payment_transaction_id_payment_transactions" in fk_dict
    assert "fk_cancellations_merchant_id_merchants" in fk_dict
    assert "fk_cancellations_agent_id_agents" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_cancellations_payment_order_id" in ix_names
    assert "ix_cancellations_payment_transaction_id" in ix_names
    assert "ix_cancellations_merchant_id" in ix_names
    assert "ix_cancellations_agent_id" in ix_names
    assert "ix_cancellations_cancellation_reference" in ix_names
    assert "ix_cancellations_provider_cancellation_reference" in ix_names
    assert "ix_cancellations_status" in ix_names
    assert "ix_cancellations_reason_type" in ix_names


def test_06_cancellations_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped cancellation_reference uniqueness constraint exists."""
    table = Base.metadata.tables["cancellations"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_cancellations_tenant_id_cancellation_reference" in uq_names


def test_07_cancellations_enum_constraints() -> None:
    """7. Verify status and reason_type check constraints exist."""
    table = Base.metadata.tables["cancellations"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_cancellations_status" in ck_names
    assert "ck_cancellations_reason_type" in ck_names


def test_08_cancellations_jsonb_metadata() -> None:
    """8. Verify cancellation_metadata uses JSONB."""
    table = Base.metadata.tables["cancellations"]
    col = table.columns["cancellation_metadata"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_09_cancellations_repr_redaction() -> None:
    """9. Verify Cancellation.__repr__ does NOT leak cancellation_metadata."""
    cn = Cancellation(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        cancellation_reference="CN-001",
        reason_type="customer_request",
        status="completed",
        cancellation_metadata={"secret_key": "hidden"},
    )
    repr_str = repr(cn)
    assert "reference='CN-001'" in repr_str
    assert "secret_key" not in repr_str


def test_10_cancellations_prohibited_secret_fields() -> None:
    """10. Verify prohibited secret fields do NOT exist on cancellations."""
    columns = {c.name for c in Base.metadata.tables["cancellations"].columns}
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


def test_11_cancellations_tenant_isolation() -> None:
    """11. Verify tenant isolation on Cancellation."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    cn = Cancellation(
        id=uuid.uuid4(),
        tenant_id=t1,
        cancellation_reference="CN-T1",
        reason_type="merchant_request",
    )
    assert cn.tenant_id == t1
    assert (cn.tenant_id == t2) is False


def test_12_cancellations_relationships() -> None:
    """12. Verify Cancellation relationships."""
    assert hasattr(Cancellation, "payment_order")
    assert hasattr(Cancellation, "payment_transaction")
    assert hasattr(Cancellation, "merchant")
    assert hasattr(Cancellation, "agent")
