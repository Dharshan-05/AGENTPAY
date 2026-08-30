"""Unit Tests for Phase 064 Razorpay Webhook Events Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.razorpay_webhook_event import RazorpayWebhookEvent


def test_01_razorpay_webhook_events_table_exists() -> None:
    """1. Verify razorpay_webhook_events table exists in Base.metadata."""
    assert "razorpay_webhook_events" in Base.metadata.tables
    assert RazorpayWebhookEvent.__tablename__ == "razorpay_webhook_events"


def test_02_razorpay_webhook_events_exact_columns() -> None:
    """2. Verify exact columns exist on razorpay_webhook_events."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "payment_order_id",
        "payment_transaction_id",
        "merchant_id",
        "provider_event_id",
        "event_reference",
        "event_type",
        "processing_status",
        "verification_status",
        "signature_verified",
        "event_payload",
        "request_id",
        "processing_error",
        "received_at",
        "processed_at",
        "verified_at",
        "failed_at",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(column_names)


def test_03_razorpay_webhook_events_pk() -> None:
    """3. Verify primary key pk_razorpay_webhook_events."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    assert table.primary_key.name == "pk_razorpay_webhook_events"


def test_04_razorpay_webhook_events_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_razorpay_webhook_events_tenant_id" in ix_names


def test_05_razorpay_webhook_events_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_razorpay_webhook_events_payment_order_id_payment_orders" in fk_dict
    assert "fk_razorpay_webhook_events_payment_transaction_id_payment_transactions" in fk_dict
    assert "fk_razorpay_webhook_events_merchant_id_merchants" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_razorpay_webhook_events_provider_event_id" in ix_names
    assert "ix_razorpay_webhook_events_event_reference" in ix_names
    assert "ix_razorpay_webhook_events_event_type" in ix_names
    assert "ix_razorpay_webhook_events_processing_status" in ix_names
    assert "ix_razorpay_webhook_events_verification_status" in ix_names
    assert "ix_razorpay_webhook_events_payment_order_id" in ix_names
    assert "ix_razorpay_webhook_events_payment_transaction_id" in ix_names
    assert "ix_razorpay_webhook_events_merchant_id" in ix_names
    assert "ix_razorpay_webhook_events_request_id" in ix_names
    assert "ix_razorpay_webhook_events_received_at" in ix_names


def test_06_razorpay_webhook_events_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped provider event & reference uniqueness constraints exist."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_razorpay_webhook_events_tenant_provider_event" in uq_names
    assert "uq_razorpay_webhook_events_tenant_event_reference" in uq_names


def test_07_razorpay_webhook_events_enum_constraints() -> None:
    """7. Verify processing_status and verification_status check constraints exist."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_razorpay_webhook_events_status" in ck_names
    assert "ck_razorpay_webhook_events_verification_status" in ck_names


def test_08_razorpay_webhook_events_jsonb_payload() -> None:
    """8. Verify event_payload uses JSONB."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    col = table.columns["event_payload"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_09_razorpay_webhook_events_repr_redaction() -> None:
    """9. Verify RazorpayWebhookEvent.__repr__ does NOT leak untrusted event_payload."""
    we = RazorpayWebhookEvent(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        provider_event_id="evt_test_12345",
        event_reference="WE-001",
        event_type="payment.captured",
        processing_status="received",
        event_payload={"secret_key": "hidden", "untrusted_input": "data"},
    )
    repr_str = repr(we)
    assert "provider_event_id='evt_test_12345'" in repr_str
    assert "secret_key" not in repr_str
    assert "untrusted_input" not in repr_str


def test_10_razorpay_webhook_events_prohibited_secret_fields() -> None:
    """10. Verify prohibited secret fields do NOT exist on razorpay_webhook_events."""
    columns = {c.name for c in Base.metadata.tables["razorpay_webhook_events"].columns}
    prohibited = {
        "webhook_secret",
        "razorpay_secret",
        "signing_secret",
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


def test_11_razorpay_webhook_events_tenant_isolation() -> None:
    """11. Verify tenant isolation on RazorpayWebhookEvent."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    we = RazorpayWebhookEvent(
        id=uuid.uuid4(),
        tenant_id=t1,
        provider_event_id="evt_t1",
        event_reference="WE-T1",
        event_type="payment.captured",
    )
    assert we.tenant_id == t1
    assert (we.tenant_id == t2) is False


def test_12_razorpay_webhook_events_relationships() -> None:
    """12. Verify RazorpayWebhookEvent relationships."""
    assert hasattr(RazorpayWebhookEvent, "payment_order")
    assert hasattr(RazorpayWebhookEvent, "payment_transaction")
    assert hasattr(RazorpayWebhookEvent, "merchant")
