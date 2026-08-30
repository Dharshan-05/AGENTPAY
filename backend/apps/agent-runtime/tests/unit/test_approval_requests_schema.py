"""Unit Tests for Phase 069 Approval Requests Schema."""

import uuid
from decimal import Decimal

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.approval_request import ApprovalRequest


def test_01_approval_requests_table_exists() -> None:
    """1. Verify approval_requests table exists in Base.metadata."""
    assert "approval_requests" in Base.metadata.tables
    assert ApprovalRequest.__tablename__ == "approval_requests"


def test_02_approval_requests_exact_columns() -> None:
    """2. Verify exact columns exist on approval_requests."""
    table = Base.metadata.tables["approval_requests"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "approval_reference",
        "approval_type",
        "status",
        "priority",
        "requested_action",
        "requested_amount",
        "currency_code",
        "requester_type",
        "requester_id",
        "target_reviewer_id",
        "required_approvals",
        "received_approvals",
        "source_type",
        "source_id",
        "security_policy_id",
        "policy_rule_id",
        "policy_evaluation_id",
        "security_violation_id",
        "risk_signal_id",
        "fraud_prediction_id",
        "commerce_transaction_id",
        "payment_order_id",
        "payment_transaction_id",
        "agent_id",
        "merchant_id",
        "request_id",
        "reason",
        "approval_context",
        "expires_at",
        "requested_at",
        "started_at",
        "resolved_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_approval_requests_pk() -> None:
    """3. Verify primary key pk_approval_requests."""
    table = Base.metadata.tables["approval_requests"]
    assert table.primary_key.name == "pk_approval_requests"


def test_04_approval_requests_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["approval_requests"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_approval_requests_tenant_id" in ix_names


def test_05_approval_requests_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["approval_requests"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_approval_requests_requester_id_users" in fk_dict
    assert "fk_approval_requests_target_reviewer_id_users" in fk_dict
    assert "fk_approval_requests_security_policy_id_security_policies" in fk_dict
    assert "fk_approval_requests_payment_order_id_payment_orders" in fk_dict
    assert "fk_approval_requests_payment_transaction_id_payment_transactions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_approval_requests_approval_reference" in ix_names
    assert "ix_approval_requests_approval_type" in ix_names
    assert "ix_approval_requests_status" in ix_names
    assert "ix_approval_requests_priority" in ix_names
    assert "ix_approval_requests_requester_id" in ix_names
    assert "ix_approval_requests_target_reviewer_id" in ix_names
    assert "ix_approval_requests_request_id" in ix_names
    assert "ix_approval_requests_expires_at" in ix_names
    assert "ix_approval_requests_requested_at" in ix_names
    assert "ix_approval_requests_source_id" in ix_names
    assert "ix_approval_requests_payment_order_id" in ix_names
    assert "ix_approval_requests_payment_transaction_id" in ix_names


def test_06_approval_requests_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped approval_reference uniqueness constraint exists."""
    table = Base.metadata.tables["approval_requests"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_approval_requests_tenant_id_approval_reference" in uq_names


def test_07_approval_requests_enum_and_counter_constraints() -> None:
    """7. Verify type, status, action, priority, threshold & counter check constraints exist."""
    table = Base.metadata.tables["approval_requests"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_approval_requests_approval_type" in ck_names
    assert "ck_approval_requests_status" in ck_names
    assert "ck_approval_requests_requested_action" in ck_names
    assert "ck_approval_requests_priority_nonnegative" in ck_names
    assert "ck_approval_requests_requested_amount_nonnegative" in ck_names
    assert "ck_approval_requests_required_approvals_positive" in ck_names
    assert "ck_approval_requests_received_approvals_nonnegative" in ck_names
    assert "ck_approval_requests_received_le_required" in ck_names


def test_08_approval_requests_numeric_precision() -> None:
    """8. Verify requested_amount uses Decimal NUMERIC(18,4) and zero FLOAT/REAL."""
    table = Base.metadata.tables["approval_requests"]
    col_type = str(table.columns["requested_amount"].type)
    assert col_type.startswith("NUMERIC(18, 4)")
    assert not col_type.startswith("FLOAT")
    assert not col_type.startswith("REAL")


def test_09_approval_requests_jsonb_context() -> None:
    """9. Verify approval_context uses JSONB."""
    table = Base.metadata.tables["approval_requests"]
    col = table.columns["approval_context"]
    assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_approval_requests_repr_redaction() -> None:
    """10. Verify ApprovalRequest.__repr__ does NOT leak approval_context."""
    ar = ApprovalRequest(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        approval_reference="AR-001",
        approval_type="payment",
        status="pending",
        requested_action="authorize",
        requested_amount=Decimal("500.0000"),
        required_approvals=2,
        received_approvals=1,
        approval_context={"secret_key": "hidden"},
    )
    repr_str = repr(ar)
    assert "reference='AR-001'" in repr_str
    assert "approvals=1/2" in repr_str
    assert "secret_key" not in repr_str


def test_11_approval_requests_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on approval_requests."""
    columns = {c.name for c in Base.metadata.tables["approval_requests"].columns}
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


def test_12_approval_requests_tenant_isolation() -> None:
    """12. Verify tenant isolation on ApprovalRequest."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    ar = ApprovalRequest(
        id=uuid.uuid4(),
        tenant_id=t1,
        approval_reference="AR-T1",
        requested_amount=Decimal("100.0000"),
    )
    assert ar.tenant_id == t1
    assert (ar.tenant_id == t2) is False


def test_13_approval_requests_relationships() -> None:
    """13. Verify ApprovalRequest relationships."""
    assert hasattr(ApprovalRequest, "requester")
    assert hasattr(ApprovalRequest, "target_reviewer")
    assert hasattr(ApprovalRequest, "security_policy")
    assert hasattr(ApprovalRequest, "policy_rule")
    assert hasattr(ApprovalRequest, "policy_evaluation")
    assert hasattr(ApprovalRequest, "security_violation")
    assert hasattr(ApprovalRequest, "risk_signal")
    assert hasattr(ApprovalRequest, "fraud_prediction")
    assert hasattr(ApprovalRequest, "commerce_transaction")
    assert hasattr(ApprovalRequest, "payment_order")
    assert hasattr(ApprovalRequest, "payment_transaction")
    assert hasattr(ApprovalRequest, "agent")
    assert hasattr(ApprovalRequest, "merchant")
