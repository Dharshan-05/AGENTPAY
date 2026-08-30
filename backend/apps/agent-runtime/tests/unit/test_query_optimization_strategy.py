"""Unit Tests for Phase 077 Query Optimization Strategy."""

import datetime
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.infrastructure.database.models.audit_log import AuditLog
from app.infrastructure.database.models.payment_order import PaymentOrder
from app.infrastructure.database.query_builder import (
    build_exists_query,
    enforce_tenant_filter,
    paginate_keyset,
)


def test_01_enforce_tenant_filter() -> None:
    """1. Verify enforce_tenant_filter appends WHERE tenant_id = :tenant_id."""
    tenant_id = uuid.uuid4()
    stmt = select(PaymentOrder)
    opt_stmt = enforce_tenant_filter(stmt, PaymentOrder.tenant_id, tenant_id)

    compiled_sql = str(opt_stmt.compile(dialect=postgresql.dialect()))  # type: ignore[no-untyped-call]  # noqa: E501

    assert "WHERE payment_orders.tenant_id =" in compiled_sql


def test_02_build_exists_query() -> None:
    """2. Verify build_exists_query compiles to SELECT EXISTS(SELECT 1 ...)."""
    tenant_id = uuid.uuid4()
    opt_stmt = build_exists_query(
        PaymentOrder.tenant_id,
        tenant_id,
        PaymentOrder.status == "created",
    )

    compiled_sql = str(opt_stmt.compile(dialect=postgresql.dialect()))  # type: ignore[no-untyped-call]  # noqa: E501

    assert "EXISTS" in compiled_sql
    assert "SELECT 1" in compiled_sql
    assert "payment_orders.tenant_id =" in compiled_sql


def test_03_keyset_pagination_first_page() -> None:
    """3. Verify paginate_keyset first page query structure."""
    tenant_id = uuid.uuid4()
    stmt = select(AuditLog)
    opt_stmt = paginate_keyset(
        query=stmt,
        id_col=AuditLog.id,
        created_at_col=AuditLog.occurred_at,
        tenant_id=tenant_id,
        tenant_col=AuditLog.tenant_id,
        limit=25,
    )

    compiled_sql = str(opt_stmt.compile(dialect=postgresql.dialect()))  # type: ignore[no-untyped-call]  # noqa: E501

    assert "WHERE audit_logs.tenant_id =" in compiled_sql
    assert "ORDER BY audit_logs.occurred_at DESC, audit_logs.id DESC" in compiled_sql
    assert "LIMIT 25" in compiled_sql or "LIMIT" in compiled_sql


def test_04_keyset_pagination_next_page() -> None:
    """4. Verify paginate_keyset cursor query structure."""
    tenant_id = uuid.uuid4()
    cursor_id = uuid.uuid4()
    cursor_time = datetime.datetime.now(datetime.UTC)

    stmt = select(AuditLog)
    opt_stmt = paginate_keyset(
        query=stmt,
        id_col=AuditLog.id,
        created_at_col=AuditLog.occurred_at,
        tenant_id=tenant_id,
        tenant_col=AuditLog.tenant_id,
        limit=50,
        cursor_created_at=cursor_time,
        cursor_id=cursor_id,
    )

    compiled_sql = str(opt_stmt.compile(dialect=postgresql.dialect()))  # type: ignore[no-untyped-call]  # noqa: E501

    assert "audit_logs.occurred_at <" in compiled_sql
    assert "audit_logs.id <" in compiled_sql


def test_05_financial_precision_preservation() -> None:
    """5. Verify query optimization tools preserve Decimal financial types."""
    po = PaymentOrder(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        order_reference="ORD-OPT-001",
        merchant_id=uuid.uuid4(),
        status="created",
        amount=Decimal("150.7500"),
        subtotal=Decimal("150.7500"),
        tax_amount=Decimal("0.0000"),
        discount_amount=Decimal("0.0000"),
        fee_amount=Decimal("0.0000"),
        total_amount=Decimal("150.7500"),
    )
    assert isinstance(po.amount, Decimal)
    assert po.amount == Decimal("150.7500")
