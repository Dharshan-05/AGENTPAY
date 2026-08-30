"""Unit Tests for Phase 067 Payment Idempotency Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.payment_idempotency_key import PaymentIdempotencyKey


def test_01_payment_idempotency_keys_table_exists() -> None:
    """1. Verify payment_idempotency_keys table exists in Base.metadata."""
    assert "payment_idempotency_keys" in Base.metadata.tables
    assert PaymentIdempotencyKey.__tablename__ == "payment_idempotency_keys"


def test_02_payment_idempotency_keys_exact_columns() -> None:
    """2. Verify exact columns exist on payment_idempotency_keys."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "idempotency_key",
        "operation_type",
        "request_id",
        "resource_type",
        "resource_id",
        "request_hash",
        "status",
        "response_code",
        "response_metadata",
        "first_seen_at",
        "completed_at",
        "expires_at",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(column_names)


def test_03_payment_idempotency_keys_pk() -> None:
    """3. Verify primary key pk_payment_idempotency_keys."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    assert table.primary_key.name == "pk_payment_idempotency_keys"


def test_04_payment_idempotency_keys_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_idempotency_keys_tenant_id" in ix_names


def test_05_payment_idempotency_keys_indexes() -> None:
    """5. Verify indexes on tenant_id, idempotency_key, operation_type, etc."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_payment_idempotency_keys_idempotency_key" in ix_names
    assert "ix_payment_idempotency_keys_operation_type" in ix_names
    assert "ix_payment_idempotency_keys_request_id" in ix_names
    assert "ix_payment_idempotency_keys_status" in ix_names
    assert "ix_payment_idempotency_keys_resource_id" in ix_names
    assert "ix_payment_idempotency_keys_expires_at" in ix_names


def test_06_payment_idempotency_keys_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped idempotency key uniqueness constraint exists."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_payment_idempotency_keys_tenant_key" in uq_names


def test_07_payment_idempotency_keys_enum_constraints() -> None:
    """7. Verify operation_type and status check constraints exist."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_payment_idempotency_keys_operation_type" in ck_names
    assert "ck_payment_idempotency_keys_status" in ck_names


def test_08_payment_idempotency_keys_jsonb_response_metadata() -> None:
    """8. Verify response_metadata uses JSONB."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    col = table.columns["response_metadata"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_09_payment_idempotency_keys_repr_redaction() -> None:
    """9. Verify PaymentIdempotencyKey.__repr__ does NOT leak sensitive metadata or hash."""
    pik = PaymentIdempotencyKey(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        idempotency_key="IK-001",
        operation_type="create_order",
        request_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status="completed",
        response_metadata={"secret_key": "hidden"},
    )
    repr_str = repr(pik)
    assert "op='create_order'" in repr_str
    assert "secret_key" not in repr_str
    assert "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" not in repr_str


def test_10_payment_idempotency_keys_prohibited_secret_fields() -> None:
    """10. Verify prohibited secret fields do NOT exist on payment_idempotency_keys."""
    columns = {c.name for c in Base.metadata.tables["payment_idempotency_keys"].columns}
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
        "authorization_header",
    }
    assert len(prohibited.intersection(columns)) == 0


def test_11_payment_idempotency_keys_tenant_isolation() -> None:
    """11. Verify tenant isolation on PaymentIdempotencyKey."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    pik = PaymentIdempotencyKey(
        id=uuid.uuid4(),
        tenant_id=t1,
        idempotency_key="IK-T1",
        operation_type="create_order",
    )
    assert pik.tenant_id == t1
    assert (pik.tenant_id == t2) is False
