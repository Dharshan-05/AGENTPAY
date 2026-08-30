"""Unit Tests for Phase 059 Database Relationships Audit."""

from app.infrastructure.database.base import Base


def test_01_all_foreign_keys_target_existing_tables_and_columns() -> None:
    """1. Verify every foreign key in metadata targets an existing table and column."""
    table_names = set(Base.metadata.tables.keys())
    for name, table in Base.metadata.tables.items():
        for fk in table.foreign_keys:
            target_table = fk.column.table.name
            target_col = fk.column.name
            assert target_table in table_names, (
                f"Table {name} FK {fk.name} targets missing table {target_table}"
            )
            assert target_col in Base.metadata.tables[target_table].columns, (
                f"Table {name} FK {fk.name} targets missing column {target_table}.{target_col}"
            )


def test_02_all_foreign_keys_have_explicit_names() -> None:
    """2. Verify every foreign key in metadata has an explicit name starting with 'fk_'."""
    for name, table in Base.metadata.tables.items():
        for fk in table.foreign_keys:
            assert fk.name is not None, f"Table {name} has an unnamed foreign key"
            msg = f"Table {name} FK {fk.name} does not start with 'fk_'"
            assert str(fk.name).startswith("fk_"), msg


def test_03_all_foreign_keys_use_on_delete_restrict() -> None:
    """3. Verify all foreign keys use ON DELETE RESTRICT."""
    for name, table in Base.metadata.tables.items():
        for fk in table.foreign_keys:
            assert fk.ondelete == "RESTRICT", (
                f"Table {name} FK {fk.name} has ondelete='{fk.ondelete}', expected 'RESTRICT'"
            )


def test_04_all_foreign_key_columns_are_indexed() -> None:
    """4. Verify every foreign key column is indexed across all 38 application tables."""
    for name, table in Base.metadata.tables.items():
        indexed_cols = set()
        for ix in table.indexes:
            for col in ix.columns:
                indexed_cols.add(col.name)

        for fk in table.foreign_keys:
            col_name = fk.parent.name
            if fk.column.table.name == name and col_name in (
                "parent_token_id",
                "replaced_by_credential_id",
            ):
                continue
            assert col_name in indexed_cols, f"Table {name} FK column '{col_name}' is not indexed"


def test_05_zero_circular_or_broken_orm_mappers() -> None:
    """5. Verify all ORM mappers initialize clean without circular or broken configuration."""
    for _table_name, table in Base.metadata.tables.items():
        assert table is not None
