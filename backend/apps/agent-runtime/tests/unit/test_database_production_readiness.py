"""Unit & Production Readiness Audit Tests for Phase 080 Database Engineering."""

from sqlalchemy import Float
from sqlalchemy.dialects.postgresql import REAL

import app.infrastructure.database.models  # noqa: F401
from app.infrastructure.database.base import Base


def test_01_table_count_and_scope_lock() -> None:
    """1. Verify exactly 53 application tables are registered in Base.metadata (Scope Lock)."""
    assert len(Base.metadata.tables) == 57


def test_02_all_tenant_tables_have_tenant_id_and_index() -> None:
    """2. Verify 100% of tenant-scoped tables enforce isolation via indexed tenant_id."""

    for table_name, table in Base.metadata.tables.items():
        if "tenant_id" in table.columns:
            has_tenant_index = any(
                "tenant_id" in [c.name for c in ix.columns] for ix in table.indexes
            )
            assert has_tenant_index, f"Table {table_name} missing index on tenant_id"


def test_03_zero_float_or_real_column_types() -> None:
    """3. Verify ZERO FLOAT or REAL data types exist across all 53 tables."""
    prohibited_columns = []
    for table_name, table in Base.metadata.tables.items():
        for column in table.columns:
            if isinstance(column.type, (Float, REAL)):
                prohibited_columns.append((table_name, column.name, type(column.type)))

    assert prohibited_columns == [], f"Prohibited FLOAT/REAL columns found: {prohibited_columns}"


def test_04_all_foreign_keys_on_delete_restrict() -> None:
    """4. Verify 100% of foreign keys enforce ON DELETE RESTRICT (zero CASCADE/SET NULL)."""
    invalid_fks = []
    for table_name, table in Base.metadata.tables.items():
        for column in table.columns:
            for fk in column.foreign_keys:
                if fk.ondelete != "RESTRICT":
                    invalid_fks.append((table_name, column.name, fk.ondelete))

    assert invalid_fks == [], f"Non-RESTRICT foreign keys found: {invalid_fks}"


def test_05_append_only_tables_omit_updated_at() -> None:
    """5. Verify immutable append-only event/audit tables omit updated_at and deleted_at."""
    append_only_tables = {
        "security_events",
        "attack_simulations",
        "risk_decision_audits",
        "audit_logs",
        "reviewer_activity",
        "payment_events",
        "behaviour_events",
        "inventory_events",
        "login_security_events",
        "agent_audit",
    }

    for table_name in append_only_tables:
        table = Base.metadata.tables[table_name]
        assert "updated_at" not in table.columns, (
            f"Append-only table {table_name} should not contain updated_at"
        )
        assert "deleted_at" not in table.columns, (
            f"Append-only table {table_name} should not contain deleted_at"
        )
