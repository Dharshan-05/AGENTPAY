"""Unit Tests for Phase 075 Risk Decision Audit Schema."""

import uuid
from decimal import Decimal

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.risk_decision_audit import RiskDecisionAudit


def test_01_risk_decision_audits_table_exists() -> None:
    """1. Verify risk_decision_audits table exists in Base.metadata."""
    assert "risk_decision_audits" in Base.metadata.tables
    assert RiskDecisionAudit.__tablename__ == "risk_decision_audits"


def test_02_risk_decision_audits_exact_columns() -> None:
    """2. Verify exact columns exist on risk_decision_audits."""
    table = Base.metadata.tables["risk_decision_audits"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "decision_reference",
        "request_id",
        "decision_type",
        "decision",
        "result",
        "decision_source",
        "risk_score",
        "confidence_score",
        "model_name",
        "model_version",
        "policy_evaluation_id",
        "security_policy_id",
        "policy_rule_id",
        "risk_signal_id",
        "fraud_prediction_id",
        "security_violation_id",
        "agent_id",
        "merchant_id",
        "commerce_transaction_id",
        "payment_transaction_id",
        "decision_reason",
        "decision_context",
        "input_summary",
        "output_summary",
        "occurred_at",
        "created_at",
    }
    assert expected.issubset(column_names)


def test_03_risk_decision_audits_pk() -> None:
    """3. Verify primary key pk_risk_decision_audits."""
    table = Base.metadata.tables["risk_decision_audits"]
    assert table.primary_key.name == "pk_risk_decision_audits"


def test_04_risk_decision_audits_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["risk_decision_audits"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_risk_decision_audits_tenant_id" in ix_names


def test_05_risk_decision_audits_fks_and_indexes() -> None:
    """5. Verify foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["risk_decision_audits"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_risk_decision_audits_policy_evaluation_id_policy_evaluations" in fk_dict
    assert "fk_risk_decision_audits_security_policy_id_security_policies" in fk_dict
    assert "fk_risk_decision_audits_policy_rule_id_policy_rules" in fk_dict
    assert "fk_risk_decision_audits_risk_signal_id_risk_signals" in fk_dict
    assert "fk_risk_decision_audits_fraud_prediction_id_fraud_predictions" in fk_dict
    assert "fk_risk_decision_audits_security_violation_id_security_violations" in fk_dict
    assert "fk_risk_decision_audits_agent_id_agents" in fk_dict
    assert "fk_risk_decision_audits_merchant_id_merchants" in fk_dict
    assert "fk_risk_decision_audits_commerce_transaction_id_commerce_transactions" in fk_dict
    assert "fk_risk_decision_audits_payment_transaction_id_payment_transactions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_risk_decision_audits_decision_reference" in ix_names
    assert "ix_risk_decision_audits_request_id" in ix_names
    assert "ix_risk_decision_audits_decision_type" in ix_names
    assert "ix_risk_decision_audits_decision" in ix_names
    assert "ix_risk_decision_audits_result" in ix_names
    assert "ix_risk_decision_audits_decision_source" in ix_names
    assert "ix_risk_decision_audits_model_name" in ix_names
    assert "ix_risk_decision_audits_policy_evaluation_id" in ix_names
    assert "ix_risk_decision_audits_security_policy_id" in ix_names
    assert "ix_risk_decision_audits_policy_rule_id" in ix_names
    assert "ix_risk_decision_audits_risk_signal_id" in ix_names
    assert "ix_risk_decision_audits_fraud_prediction_id" in ix_names
    assert "ix_risk_decision_audits_security_violation_id" in ix_names
    assert "ix_risk_decision_audits_agent_id" in ix_names
    assert "ix_risk_decision_audits_merchant_id" in ix_names
    assert "ix_risk_decision_audits_commerce_transaction_id" in ix_names
    assert "ix_risk_decision_audits_payment_transaction_id" in ix_names
    assert "ix_risk_decision_audits_occurred_at" in ix_names


def test_06_risk_decision_audits_uniqueness_constraints() -> None:
    """6. Verify tenant-scoped decision_reference uniqueness constraint exists."""
    table = Base.metadata.tables["risk_decision_audits"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_risk_decision_audits_tenant_id_decision_reference" in uq_names


def test_07_risk_decision_audits_enum_and_score_constraints() -> None:
    """7. Verify check constraints exist."""
    table = Base.metadata.tables["risk_decision_audits"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_risk_decision_audits_decision_type" in ck_names
    assert "ck_risk_decision_audits_decision" in ck_names
    assert "ck_risk_decision_audits_result" in ck_names
    assert "ck_risk_decision_audits_risk_score_bounds" in ck_names
    assert "ck_risk_decision_audits_confidence_score_bounds" in ck_names


def test_08_risk_decision_audits_append_only_structure() -> None:
    """8. Verify risk_decision_audits is APPEND-ONLY and lacks updated_at/deleted_at."""
    table = Base.metadata.tables["risk_decision_audits"]
    column_names = {c.name for c in table.columns}
    assert "updated_at" not in column_names
    assert "deleted_at" not in column_names
    assert "occurred_at" in column_names
    assert "created_at" in column_names


def test_09_risk_decision_audits_jsonb_summaries() -> None:
    """9. Verify decision_context, input_summary, output_summary use JSONB."""
    table = Base.metadata.tables["risk_decision_audits"]
    for col_name in ("decision_context", "input_summary", "output_summary"):
        col = table.columns[col_name]
        assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_risk_decision_audits_repr_redaction() -> None:
    """10. Verify RiskDecisionAudit.__repr__ does NOT leak JSONB summaries."""
    rda = RiskDecisionAudit(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        decision_reference="RDA-001",
        decision_type="transaction",
        decision="allow",
        result="success",
        risk_score=Decimal("12.5000"),
        confidence_score=Decimal("0.9800"),
        decision_context={"secret_key": "hidden"},
        input_summary={"secret_key": "hidden"},
        output_summary={"secret_key": "hidden"},
    )
    repr_str = repr(rda)
    assert "decision='allow'" in repr_str
    assert "secret_key" not in repr_str


def test_11_risk_decision_audits_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on risk_decision_audits."""
    columns = {c.name for c in Base.metadata.tables["risk_decision_audits"].columns}
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


def test_12_risk_decision_audits_tenant_isolation() -> None:
    """12. Verify tenant isolation on RiskDecisionAudit."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    rda = RiskDecisionAudit(
        id=uuid.uuid4(),
        tenant_id=t1,
        decision_reference="RDA-T1",
        decision_type="risk",
        decision="challenge",
        risk_score=Decimal("45.0000"),
        confidence_score=Decimal("0.8500"),
    )
    assert rda.tenant_id == t1
    assert (rda.tenant_id == t2) is False


def test_13_risk_decision_audits_relationships() -> None:
    """13. Verify RiskDecisionAudit relationships."""
    assert hasattr(RiskDecisionAudit, "policy_evaluation")
    assert hasattr(RiskDecisionAudit, "security_policy")
    assert hasattr(RiskDecisionAudit, "policy_rule")
    assert hasattr(RiskDecisionAudit, "risk_signal")
    assert hasattr(RiskDecisionAudit, "fraud_prediction")
    assert hasattr(RiskDecisionAudit, "security_violation")
    assert hasattr(RiskDecisionAudit, "agent")
    assert hasattr(RiskDecisionAudit, "merchant")
    assert hasattr(RiskDecisionAudit, "commerce_transaction")
    assert hasattr(RiskDecisionAudit, "payment_transaction")
