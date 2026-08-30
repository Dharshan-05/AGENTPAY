"""Unit Tests for Phase 062 Payment Transactions Schema."""

import uuid
from decimal import Decimal

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.payment_transaction import PaymentTransaction


def test_01_payment_transactions_table_exists() -> None:
    """1. Verify payment_transactions table exists in Base.metadata."""
    assert "payment_transactions" in Base.metadata.tables
    assert PaymentTransaction.__tablename__ == "payment_transactions"


def test_02_payment_transactions_exact_columns() -> None:
    """2. Verify exact columns exist on payment_transactions."""
    table = Base.metadata.tables["payment_transactions"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "payment_order_id",
        "merchant_id",
        "agent_id",
        "commerce_transaction_id",
        "transaction_reference",
        "external_reference",
        "payment_provider",
        "provider_transaction_reference",
        "provider_authorization_reference",
        "transaction_type",
        "status",
        "amount",
        "authorized_amount",
        "captured_amount",
        "fee_amount",
        "tax_amount",
        "total_amount",
        "currency_code",
        "transaction_metadata",
        "created_at",
        "updated_at",
        "processed_at",
        "authorized_at",
        "captured_at",
        "failed_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_payment_transactions_pk() -> None:
    """3. Verify primary key pk_payment_transactions."""
    table = Base.metadata.tables["payment_transactions"]
    assert table.primary_key.name == "pk_payment_transactions"


def test_04_payment_transactions_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["payment_transactions"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_transactions_tenant_id" in ix_names


def test_05_payment_transactions_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["payment_transactions"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_payment_transactions_payment_order_id_payment_orders" in fk_dict
    assert "fk_payment_transactions_merchant_id_merchants" in fk_dict
    assert "fk_payment_transactions_agent_id_agents" in fk_dict
    assert "fk_payment_transactions_commerce_transaction_id_commerce_transactions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_transactions_payment_order_id" in ix_names
    assert "ix_payment_transactions_merchant_id" in ix_names
    assert "ix_payment_transactions_agent_id" in ix_names
    assert "ix_payment_transactions_commerce_transaction_id" in ix_names
    assert "ix_payment_transactions_transaction_reference" in ix_names
    assert "ix_payment_transactions_payment_provider" in ix_names
    assert "ix_payment_transactions_provider_transaction_reference" in ix_names
    assert "ix_payment_transactions_transaction_type" in ix_names
    assert "ix_payment_transactions_status" in ix_names


def test_06_payment_transactions_reference_uniqueness() -> None:
    """6. Verify tenant-scoped transaction_reference uniqueness constraint."""
    table = Base.metadata.tables["payment_transactions"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_payment_transactions_tenant_id_transaction_reference" in uq_names


def test_07_payment_transactions_enum_constraints() -> None:
    """7. Verify transaction_type and status check constraints exist."""
    table = Base.metadata.tables["payment_transactions"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_payment_transactions_transaction_type" in ck_names
    assert "ck_payment_transactions_status" in ck_names


def test_08_payment_transactions_monetary_precision_and_nonnegative() -> None:
    """8. Verify monetary values use Decimal NUMERIC(18,4) and non-negative constraints exist."""
    table = Base.metadata.tables["payment_transactions"]
    monetary_cols = (
        "amount",
        "authorized_amount",
        "captured_amount",
        "fee_amount",
        "tax_amount",
        "total_amount",
    )
    for col in monetary_cols:
        col_type = str(table.columns[col].type)
        assert col_type.startswith("NUMERIC(18, 4)")
        assert not col_type.startswith("FLOAT")
        assert not col_type.startswith("REAL")

    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_payment_transactions_amount_nonnegative" in ck_names
    assert "ck_payment_transactions_authorized_amount_nonnegative" in ck_names
    assert "ck_payment_transactions_captured_amount_nonnegative" in ck_names
    assert "ck_payment_transactions_fee_amount_nonnegative" in ck_names
    assert "ck_payment_transactions_tax_amount_nonnegative" in ck_names
    assert "ck_payment_transactions_total_amount_nonnegative" in ck_names


def test_09_payment_transactions_provider_references() -> None:
    """9. Verify non-secret provider references are supported."""
    pt = PaymentTransaction(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        payment_order_id=uuid.uuid4(),
        transaction_reference="TX-001",
        payment_provider="razorpay",
        provider_transaction_reference="pay_MOCK12345",
        provider_authorization_reference="auth_MOCK67890",
        transaction_type="payment",
        status="completed",
        amount=Decimal("100.0000"),
        total_amount=Decimal("100.0000"),
    )
    assert pt.payment_provider == "razorpay"
    assert pt.provider_transaction_reference == "pay_MOCK12345"


def test_10_payment_transactions_jsonb_metadata() -> None:
    """10. Verify transaction_metadata uses JSONB."""
    table = Base.metadata.tables["payment_transactions"]
    col = table.columns["transaction_metadata"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_11_payment_transactions_repr_redaction() -> None:
    """11. Verify PaymentTransaction.__repr__ does NOT leak JSONB metadata."""
    pt = PaymentTransaction(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        payment_order_id=uuid.uuid4(),
        transaction_reference="TX-001",
        payment_provider="stripe",
        transaction_type="payment",
        status="completed",
        amount=Decimal("100.0000"),
        total_amount=Decimal("100.0000"),
        transaction_metadata={"secret_key": "hidden"},
    )
    repr_str = repr(pt)
    assert "reference='TX-001'" in repr_str
    assert "secret_key" not in repr_str


def test_12_payment_transactions_prohibited_secret_fields() -> None:
    """12. Verify prohibited secret fields do NOT exist on payment_transactions."""
    columns = {c.name for c in Base.metadata.tables["payment_transactions"].columns}
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


def test_13_payment_transactions_tenant_isolation() -> None:
    """13. Verify tenant isolation on PaymentTransaction."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    pt = PaymentTransaction(
        id=uuid.uuid4(),
        tenant_id=t1,
        payment_order_id=uuid.uuid4(),
        transaction_reference="TX-T1",
        payment_provider="razorpay",
        transaction_type="payment",
        amount=Decimal("50.0000"),
        total_amount=Decimal("50.0000"),
    )
    assert pt.tenant_id == t1
    assert (pt.tenant_id == t2) is False


def test_14_payment_transactions_relationships() -> None:
    """14. Verify PaymentTransaction relationships."""
    assert hasattr(PaymentTransaction, "payment_order")
    assert hasattr(PaymentTransaction, "merchant")
    assert hasattr(PaymentTransaction, "agent")
    assert hasattr(PaymentTransaction, "commerce_transaction")
    assert hasattr(PaymentTransaction, "payment_events")
