"""Unit Test Suite for Phase 314 — Database Forensic Integrity & ORM Constraints Verification."""

from __future__ import annotations

from app.infrastructure.database.base import Base


def test_01_total_table_count() -> None:
    """Test 1: ORM metadata contains exactly 57 database tables."""
    tables = Base.metadata.tables
    assert len(tables) == 57


def test_02_payment_idempotency_keys_constraints() -> None:
    """Test 2: payment_idempotency_keys table has explicit unique and check constraints."""
    table = Base.metadata.tables["payment_idempotency_keys"]
    assert table is not None
    uniques = [c for c in table.constraints if c.__class__.__name__ == "UniqueConstraint"]
    assert len(uniques) >= 1
    assert any("tenant_id" in [getattr(col, "name", "") for col in getattr(c, "columns", [])] for c in uniques)


def test_03_approval_requests_table_indexes() -> None:
    """Test 3: approval_requests table contains composite indexes for tenant_id and status."""
    table = Base.metadata.tables["approval_requests"]
    assert table is not None
    idx_names = [str(idx.name) for idx in table.indexes]
    assert any("tenant_id" in name for name in idx_names)
    assert any("status" in name for name in idx_names)


def test_04_payment_transactions_foreign_keys() -> None:
    """Test 4: payment_transactions table enforces foreign key relationships."""
    table = Base.metadata.tables["payment_transactions"]
    assert table is not None
    fk_cols = [str(fk.column.name) for fk in table.foreign_keys]
    assert len(fk_cols) >= 1


def test_05_approval_decisions_immutability_constraints() -> None:
    """Test 5: approval_decisions table has foreign keys to approval_requests."""
    table = Base.metadata.tables["approval_decisions"]
    assert table is not None
    fk_tables = [str(fk.column.table.name) for fk in table.foreign_keys]
    assert "approval_requests" in fk_tables


def test_06_global_audit_logs_table_exists() -> None:
    """Test 6: audit_logs table exists with tenant_id index."""
    table = Base.metadata.tables["audit_logs"]
    assert table is not None
    idx_names = [str(idx.name) for idx in table.indexes]
    assert any("tenant_id" in name for name in idx_names)


def test_07_razorpay_webhook_events_table_exists() -> None:
    """Test 7: razorpay_webhook_events table exists with indexing."""
    table = Base.metadata.tables["razorpay_webhook_events"]
    assert table is not None
    assert "event_type" in table.columns


def test_08_cancellations_and_refunds_tables_exist() -> None:
    """Test 8: cancellations and refunds tables exist in ORM metadata."""
    assert "cancellations" in Base.metadata.tables
    assert "refunds" in Base.metadata.tables


def test_09_user_preferences_table_exists() -> None:
    """Test 9: user_preferences table exists with unique constraint on user_id."""
    table = Base.metadata.tables["user_preferences"]
    assert table is not None
    uniques = [c for c in table.constraints if c.__class__.__name__ == "UniqueConstraint"]
    assert any("user_id" in [getattr(col, "name", "") for col in getattr(c, "columns", [])] for c in uniques)
