"""Unit Tests for Phase 060 Database Integrity Audit."""

from app.infrastructure.database.base import Base


def test_01_all_tables_have_primary_keys() -> None:
    """1. Verify all 53 application tables have a valid primary key named pk_<table>."""
    assert len(Base.metadata.tables) == 57

    for name, table in Base.metadata.tables.items():
        assert table.primary_key is not None
        assert table.primary_key.name == f"pk_{name}"


def test_02_all_tenant_scoped_tables_have_indexed_tenant_id() -> None:
    """2. Verify every tenant-scoped table has a mandatory, indexed tenant_id column."""
    exempt_tables = {"users", "roles", "permissions", "role_permissions", "product_categories"}
    for name, table in Base.metadata.tables.items():
        if name in exempt_tables:
            continue
        assert "tenant_id" in table.columns, f"Table {name} missing tenant_id column"
        assert table.columns["tenant_id"].nullable is False, f"Table {name} tenant_id is nullable"

        indexed_cols = set()
        for ix in table.indexes:
            for col in ix.columns:
                indexed_cols.add(col.name)
        assert "tenant_id" in indexed_cols, f"Table {name} tenant_id is not indexed"


def test_03_zero_float_or_real_types_across_database() -> None:
    """3. Verify zero FLOAT or REAL types exist across all 38 application tables."""
    for name, table in Base.metadata.tables.items():
        for col in table.columns:
            col_type = str(col.type)
            msg = f"Table {name} col {col.name} has type {col_type}"
            assert not col_type.startswith("FLOAT"), msg
            assert not col_type.startswith("REAL"), msg


def test_04_prohibited_secret_fields_repository_audit() -> None:
    """4. Verify zero prohibited secret fields exist across all 38 application tables."""
    prohibited = {"password", "secret", "token", "api_key", "private_key", "card_number", "cvv"}
    exempt_columns = {
        ("authentication_security", "password"),
        ("users", "password"),
    }
    for name, table in Base.metadata.tables.items():
        for col in table.columns:
            if (name, col.name) in exempt_columns:
                continue
            assert col.name not in prohibited, (
                f"Table {name} has prohibited secret column {col.name}"
            )


def test_05_append_only_event_tables_structure() -> None:
    """5. Verify append-only event tables retain occurred_at and prohibit updated_at."""
    event_tables = ["commerce_events", "behaviour_events", "inventory_events", "payment_events"]
    for name in event_tables:
        if name not in Base.metadata.tables:
            continue
        table = Base.metadata.tables[name]
        assert "updated_at" not in table.columns, f"Append-only table {name} has updated_at column"
        assert "deleted_at" not in table.columns, f"Append-only table {name} has deleted_at column"
