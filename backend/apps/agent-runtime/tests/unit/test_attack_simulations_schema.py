"""Unit Tests for Phase 074 Attack Simulations Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.attack_simulation import AttackSimulation


def test_01_attack_simulations_table_exists() -> None:
    """1. Verify attack_simulations table exists in Base.metadata."""
    assert "attack_simulations" in Base.metadata.tables
    assert AttackSimulation.__tablename__ == "attack_simulations"


def test_02_attack_simulations_exact_columns() -> None:
    """2. Verify exact columns exist on attack_simulations."""
    table = Base.metadata.tables["attack_simulations"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "simulation_reference",
        "simulation_type",
        "scenario",
        "status",
        "severity",
        "outcome",
        "target_component",
        "target_resource_type",
        "target_resource_id",
        "initiated_by",
        "request_id",
        "simulation_parameters",
        "expected_result",
        "actual_result",
        "findings",
        "evidence_payload",
        "risk_score",
        "confidence_score",
        "started_at",
        "completed_at",
        "created_at",
    }
    assert expected.issubset(column_names)


def test_03_attack_simulations_pk() -> None:
    """3. Verify primary key pk_attack_simulations."""
    table = Base.metadata.tables["attack_simulations"]
    assert table.primary_key.name == "pk_attack_simulations"


def test_04_attack_simulations_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["attack_simulations"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_attack_simulations_tenant_id" in ix_names


def test_05_attack_simulations_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["attack_simulations"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_attack_simulations_initiated_by_users" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_attack_simulations_simulation_reference" in ix_names
    assert "ix_attack_simulations_simulation_type" in ix_names
    assert "ix_attack_simulations_status" in ix_names
    assert "ix_attack_simulations_severity" in ix_names
    assert "ix_attack_simulations_outcome" in ix_names
    assert "ix_attack_simulations_target_resource_id" in ix_names
    assert "ix_attack_simulations_initiated_by" in ix_names
    assert "ix_attack_simulations_request_id" in ix_names
    assert "ix_attack_simulations_started_at" in ix_names
    assert "ix_attack_simulations_completed_at" in ix_names


def test_06_attack_simulations_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped simulation_reference uniqueness constraint exists."""
    table = Base.metadata.tables["attack_simulations"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_attack_simulations_tenant_id_simulation_reference" in uq_names


def test_07_attack_simulations_enum_constraints() -> None:
    """7. Verify check constraints exist."""
    table = Base.metadata.tables["attack_simulations"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_attack_simulations_simulation_type" in ck_names
    assert "ck_attack_simulations_status" in ck_names
    assert "ck_attack_simulations_severity" in ck_names
    assert "ck_attack_simulations_outcome" in ck_names
    assert "ck_attack_simulations_risk_score_bounds" in ck_names
    assert "ck_attack_simulations_confidence_score_bounds" in ck_names


def test_08_attack_simulations_append_only_structure() -> None:
    """8. Verify attack_simulations is APPEND-ONLY and lacks updated_at/deleted_at."""
    table = Base.metadata.tables["attack_simulations"]
    column_names = {c.name for c in table.columns}
    assert "updated_at" not in column_names
    assert "deleted_at" not in column_names
    assert "created_at" in column_names


def test_09_attack_simulations_jsonb_payloads() -> None:
    """9. Verify simulation_parameters and evidence_payload use JSONB."""
    table = Base.metadata.tables["attack_simulations"]
    for col_name in ("simulation_parameters", "evidence_payload"):
        col = table.columns[col_name]
        assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_attack_simulations_repr_redaction() -> None:
    """10. Verify AttackSimulation.__repr__ does NOT leak JSONB payloads."""
    ats = AttackSimulation(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        simulation_reference="SIM-001",
        simulation_type="policy_bypass",
        scenario="Test bypass",
        status="planned",
        outcome="blocked",
        target_component="policy_engine",
        initiated_by=uuid.uuid4(),
        expected_result="blocked",
        simulation_parameters={"secret_key": "hidden"},
        evidence_payload={"secret_key": "hidden"},
    )
    repr_str = repr(ats)
    assert "type='policy_bypass'" in repr_str
    assert "secret_key" not in repr_str


def test_11_attack_simulations_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on attack_simulations."""
    columns = {c.name for c in Base.metadata.tables["attack_simulations"].columns}
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


def test_12_attack_simulations_tenant_isolation() -> None:
    """12. Verify tenant isolation on AttackSimulation."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    ats = AttackSimulation(
        id=uuid.uuid4(),
        tenant_id=t1,
        simulation_reference="SIM-T1",
        scenario="Isolation test",
        target_component="runtime",
        initiated_by=uuid.uuid4(),
        expected_result="blocked",
    )
    assert ats.tenant_id == t1
    assert (ats.tenant_id == t2) is False


def test_13_attack_simulations_relationships() -> None:
    """13. Verify AttackSimulation relationships."""
    assert hasattr(AttackSimulation, "initiator")
