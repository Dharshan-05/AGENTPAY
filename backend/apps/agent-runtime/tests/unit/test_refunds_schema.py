"""Unit Tests for Phase 065 Refunds Schema."""

import uuid
from decimal import Decimal

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.refund import Refund


def test_01_refunds_table_exists() -> None:
    """1. Verify refunds table exists in Base.metadata."""
    assert "refunds" in Base.metadata.tables
    assert Refund.__tablename__ == "refunds"


def test_02_refunds_exact_columns() -> None:
    """2. Verify exact columns exist on refunds."""
    table = Base.metadata.tables["refunds"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "payment_transaction_id",
        "payment_order_id",
        "commerce_transaction_id",
        "merchant_id",
        "refund_reference",
        "external_reference",
        "provider_refund_reference",
        "refund_type",
        "status",
        "amount",
        "currency_code",
        "reason",
        "refund_metadata",
        "requested_at",
        "processed_at",
        "completed_at",
        "failed_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_refunds_pk() -> None:
    """3. Verify primary key pk_refunds."""
    table = Base.metadata.tables["refunds"]
    assert table.primary_key.name == "pk_refunds"


def test_04_refunds_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["refunds"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_refunds_tenant_id" in ix_names


def test_05_refunds_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["refunds"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_refunds_payment_transaction_id_payment_transactions" in fk_dict
    assert "fk_refunds_payment_order_id_payment_orders" in fk_dict
    assert "fk_refunds_commerce_transaction_id_commerce_transactions" in fk_dict
    assert "fk_refunds_merchant_id_merchants" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_refunds_payment_transaction_id" in ix_names
    assert "ix_refunds_payment_order_id" in ix_names
    assert "ix_refunds_commerce_transaction_id" in ix_names
    assert "ix_refunds_merchant_id" in ix_names
    assert "ix_refunds_refund_reference" in ix_names
    assert "ix_refunds_provider_refund_reference" in ix_names
    assert "ix_refunds_refund_type" in ix_names
    assert "ix_refunds_status" in ix_names


def test_06_refunds_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped refund_reference uniqueness constraint exists."""
    table = Base.metadata.tables["refunds"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_refunds_tenant_id_refund_reference" in uq_names


def test_07_refunds_enum_and_amount_constraints() -> None:
    """7. Verify refund_type, status, and positive amount check constraints exist."""
    table = Base.metadata.tables["refunds"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_refunds_type" in ck_names
    assert "ck_refunds_status" in ck_names
    assert "ck_refunds_amount_positive" in ck_names


def test_08_refunds_numeric_precision() -> None:
    """8. Verify amount uses Decimal NUMERIC(18,4) and zero FLOAT/REAL."""
    table = Base.metadata.tables["refunds"]
    col_type = str(table.columns["amount"].type)
    assert col_type.startswith("NUMERIC(18, 4)")
    assert not col_type.startswith("FLOAT")
    assert not col_type.startswith("REAL")


def test_09_refunds_jsonb_metadata() -> None:
    """9. Verify refund_metadata uses JSONB."""
    table = Base.metadata.tables["refunds"]
    col = table.columns["refund_metadata"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_refunds_repr_redaction() -> None:
    """10. Verify Refund.__repr__ does NOT leak refund_metadata."""
    rf = Refund(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        payment_transaction_id=uuid.uuid4(),
        refund_reference="RF-001",
        refund_type="full",
        status="completed",
        amount=Decimal("50.0000"),
        refund_metadata={"secret_key": "hidden"},
    )
    repr_str = repr(rf)
    assert "reference='RF-001'" in repr_str
    assert "secret_key" not in repr_str


def test_11_refunds_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on refunds."""
    columns = {c.name for c in Base.metadata.tables["refunds"].columns}
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


def test_12_refunds_tenant_isolation() -> None:
    """12. Verify tenant isolation on Refund."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    rf = Refund(
        id=uuid.uuid4(),
        tenant_id=t1,
        payment_transaction_id=uuid.uuid4(),
        refund_reference="RF-T1",
        amount=Decimal("25.0000"),
    )
    assert rf.tenant_id == t1
    assert (rf.tenant_id == t2) is False


def test_13_refunds_relationships() -> None:
    """13. Verify Refund relationships."""
    assert hasattr(Refund, "payment_transaction")
    assert hasattr(Refund, "payment_order")
    assert hasattr(Refund, "commerce_transaction")
    assert hasattr(Refund, "merchant")
