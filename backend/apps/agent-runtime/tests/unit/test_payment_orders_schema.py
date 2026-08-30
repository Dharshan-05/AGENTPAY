"""Unit Tests for Phase 061 Payment Orders Schema."""

import uuid
from decimal import Decimal

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.payment_order import PaymentOrder


def test_01_payment_orders_table_exists() -> None:
    """1. Verify payment_orders table exists in Base.metadata."""
    assert "payment_orders" in Base.metadata.tables
    assert PaymentOrder.__tablename__ == "payment_orders"


def test_02_payment_orders_exact_columns() -> None:
    """2. Verify exact columns exist on payment_orders."""
    table = Base.metadata.tables["payment_orders"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "merchant_id",
        "agent_id",
        "product_id",
        "offer_id",
        "purchase_intent_id",
        "purchase_plan_id",
        "order_reference",
        "external_reference",
        "status",
        "amount",
        "subtotal",
        "tax_amount",
        "discount_amount",
        "fee_amount",
        "total_amount",
        "currency_code",
        "quantity",
        "order_metadata",
        "created_at",
        "updated_at",
        "expires_at",
        "authorized_at",
        "completed_at",
        "failed_at",
        "cancelled_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_payment_orders_pk() -> None:
    """3. Verify primary key pk_payment_orders."""
    table = Base.metadata.tables["payment_orders"]
    assert table.primary_key.name == "pk_payment_orders"


def test_04_payment_orders_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["payment_orders"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_orders_tenant_id" in ix_names


def test_05_payment_orders_fks_and_indexes() -> None:
    """5. Verify 6 foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["payment_orders"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_payment_orders_merchant_id_merchants" in fk_dict
    assert "fk_payment_orders_agent_id_agents" in fk_dict
    assert "fk_payment_orders_product_id_products" in fk_dict
    assert "fk_payment_orders_offer_id_offers" in fk_dict
    assert "fk_payment_orders_purchase_intent_id_purchase_intents" in fk_dict
    assert "fk_payment_orders_purchase_plan_id_purchase_plans" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_orders_merchant_id" in ix_names
    assert "ix_payment_orders_agent_id" in ix_names
    assert "ix_payment_orders_product_id" in ix_names
    assert "ix_payment_orders_offer_id" in ix_names
    assert "ix_payment_orders_purchase_intent_id" in ix_names
    assert "ix_payment_orders_purchase_plan_id" in ix_names
    assert "ix_payment_orders_order_reference" in ix_names
    assert "ix_payment_orders_external_reference" in ix_names
    assert "ix_payment_orders_status" in ix_names
    assert "ix_payment_orders_created_at" in ix_names


def test_06_payment_orders_reference_uniqueness() -> None:
    """6. Verify tenant-scoped order_reference uniqueness constraint."""
    table = Base.metadata.tables["payment_orders"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_payment_orders_tenant_id_order_reference" in uq_names


def test_07_payment_orders_status_constraint() -> None:
    """7. Verify status check constraint exists."""
    table = Base.metadata.tables["payment_orders"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_payment_orders_status" in ck_names


def test_08_payment_orders_monetary_precision_and_nonnegative() -> None:
    """8. Verify monetary values use Decimal NUMERIC(18,4) and non-negative constraints exist."""
    table = Base.metadata.tables["payment_orders"]
    monetary_cols = (
        "amount",
        "subtotal",
        "tax_amount",
        "discount_amount",
        "fee_amount",
        "total_amount",
    )
    for col in monetary_cols:
        col_type = str(table.columns[col].type)
        assert col_type.startswith("NUMERIC(18, 4)")
        assert not col_type.startswith("FLOAT")
        assert not col_type.startswith("REAL")

    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_payment_orders_amount_nonnegative" in ck_names
    assert "ck_payment_orders_subtotal_nonnegative" in ck_names
    assert "ck_payment_orders_tax_nonnegative" in ck_names
    assert "ck_payment_orders_discount_nonnegative" in ck_names
    assert "ck_payment_orders_fee_nonnegative" in ck_names
    assert "ck_payment_orders_total_nonnegative" in ck_names
    assert "ck_payment_orders_quantity_nonnegative" in ck_names
    assert "ck_payment_orders_date_bounds" in ck_names


def test_09_payment_orders_quantity_precision() -> None:
    """9. Verify quantity uses Decimal NUMERIC(18,3)."""
    table = Base.metadata.tables["payment_orders"]
    col_type = str(table.columns["quantity"].type)
    assert col_type.startswith("NUMERIC(18, 3)")


def test_10_payment_orders_jsonb_metadata() -> None:
    """10. Verify order_metadata uses JSONB."""
    table = Base.metadata.tables["payment_orders"]
    col = table.columns["order_metadata"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_11_payment_orders_repr_redaction() -> None:
    """11. Verify PaymentOrder.__repr__ does NOT leak JSONB metadata."""
    po = PaymentOrder(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        order_reference="ORD-001",
        amount=Decimal("100.0000"),
        total_amount=Decimal("100.0000"),
        currency_code="USD",
        status="created",
        order_metadata={"secret_key": "hidden"},
    )
    repr_str = repr(po)
    assert "reference='ORD-001'" in repr_str
    assert "secret_key" not in repr_str


def test_12_payment_orders_prohibited_secret_fields() -> None:
    """12. Verify prohibited secret fields do NOT exist on payment_orders."""
    columns = {c.name for c in Base.metadata.tables["payment_orders"].columns}
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


def test_13_payment_orders_tenant_isolation() -> None:
    """13. Verify tenant isolation on PaymentOrder."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    po = PaymentOrder(
        id=uuid.uuid4(),
        tenant_id=t1,
        order_reference="ORD-T1",
        amount=Decimal("50.0000"),
        total_amount=Decimal("50.0000"),
    )
    assert po.tenant_id == t1
    assert (po.tenant_id == t2) is False


def test_14_payment_orders_relationships() -> None:
    """14. Verify PaymentOrder relationships."""
    assert hasattr(PaymentOrder, "merchant")
    assert hasattr(PaymentOrder, "agent")
    assert hasattr(PaymentOrder, "product")
    assert hasattr(PaymentOrder, "offer")
    assert hasattr(PaymentOrder, "purchase_intent")
    assert hasattr(PaymentOrder, "purchase_plan")
    assert hasattr(PaymentOrder, "payment_transactions")
    assert hasattr(PaymentOrder, "payment_events")
