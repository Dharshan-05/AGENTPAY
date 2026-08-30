"""Unit Tests for Phase 076 Database Indexing Strategy."""

from app.infrastructure.database.base import Base


def test_01_all_foreign_keys_have_indexes() -> None:
    """1. Verify 100% of foreign key columns across all 53 tables have an index."""
    unindexed_fks = []
    for table_name, table in Base.metadata.tables.items():
        for column in table.columns:
            if column.foreign_keys:
                has_index = any(column.name in [c.name for c in ix.columns] for ix in table.indexes)
                if not has_index:
                    unindexed_fks.append((table_name, column.name))

    assert unindexed_fks == [], f"Found unindexed FK columns: {unindexed_fks}"


def test_02_all_tenant_id_columns_have_indexes() -> None:
    """2. Verify 100% of tenant_id columns across all tables have an index."""
    unindexed_tenants = []
    for table_name, table in Base.metadata.tables.items():
        if "tenant_id" in table.columns:
            has_tenant_index = any(
                "tenant_id" in [c.name for c in ix.columns] for ix in table.indexes
            )
            if not has_tenant_index:
                unindexed_tenants.append(table_name)

    assert unindexed_tenants == [], f"Found unindexed tenant_id tables: {unindexed_tenants}"


def test_03_strategic_composite_indexes_exist() -> None:
    """3. Verify key composite indexes exist on critical operational tables."""
    composite_index_checks = {
        "payment_orders": "ix_payment_orders_tenant_status",
        "payment_transactions": "ix_payment_transactions_tenant_status",
        "review_queue": "ix_review_queue_tenant_status_priority",
        "approval_requests": "ix_approval_requests_tenant_status",
        "audit_logs": "ix_audit_logs_tenant_occurred_at",
        "security_events": "ix_security_events_tenant_occurred_at",
        "risk_decision_audits": "ix_risk_decision_audits_tenant_occurred_at",
    }

    for table_name, expected_ix_name in composite_index_checks.items():
        table = Base.metadata.tables[table_name]
        ix_names = {ix.name for ix in table.indexes}
        assert expected_ix_name in ix_names, (
            f"Missing expected composite index {expected_ix_name} on {table_name}"
        )


def test_04_no_duplicate_indexes() -> None:
    """4. Verify no duplicate index definitions exist on any table."""
    for table_name, table in Base.metadata.tables.items():
        index_signatures = []
        for ix in table.indexes:
            sig = (tuple(c.name for c in ix.columns), ix.unique)
            assert sig not in index_signatures, (
                f"Duplicate index signature {sig} on table {table_name}"
            )
            index_signatures.append(sig)
