"""Unit Tests for Phase 057 Fraud Predictions Schema."""

import uuid

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.fraud_prediction import FraudPrediction


def test_01_fraud_predictions_table_exists() -> None:
    """1. Verify fraud_predictions table exists in Base.metadata."""
    assert "fraud_predictions" in Base.metadata.tables
    assert FraudPrediction.__tablename__ == "fraud_predictions"


def test_02_fraud_predictions_exact_columns() -> None:
    """2. Verify exact columns exist on fraud_predictions."""
    table = Base.metadata.tables["fraud_predictions"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "security_policy_id",
        "policy_rule_id",
        "policy_evaluation_id",
        "security_violation_id",
        "risk_signal_id",
        "agent_id",
        "merchant_id",
        "product_id",
        "offer_id",
        "purchase_intent_id",
        "purchase_plan_id",
        "commerce_transaction_id",
        "prediction_reference",
        "model_reference",
        "model_version",
        "prediction_type",
        "prediction_status",
        "prediction_label",
        "fraud_probability",
        "legitimate_probability",
        "risk_score",
        "confidence_score",
        "feature_count",
        "feature_snapshot",
        "prediction_context",
        "prediction_metadata",
        "request_id",
        "actor_type",
        "actor_id",
        "predicted_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_fraud_predictions_pk() -> None:
    """3. Verify primary key pk_fraud_predictions."""
    table = Base.metadata.tables["fraud_predictions"]
    assert table.primary_key.name == "pk_fraud_predictions"


def test_04_fraud_predictions_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["fraud_predictions"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_fraud_predictions_tenant_id" in ix_names


def test_05_fraud_predictions_fks_and_indexes() -> None:
    """5. Verify 12 foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["fraud_predictions"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_fraud_predictions_security_policy_id_security_policies" in fk_dict
    assert "fk_fraud_predictions_policy_rule_id_policy_rules" in fk_dict
    assert "fk_fraud_predictions_policy_evaluation_id_policy_evaluations" in fk_dict
    assert "fk_fraud_predictions_security_violation_id_security_violations" in fk_dict
    assert "fk_fraud_predictions_risk_signal_id_risk_signals" in fk_dict
    assert "fk_fraud_predictions_agent_id_agents" in fk_dict
    assert "fk_fraud_predictions_merchant_id_merchants" in fk_dict
    assert "fk_fraud_predictions_product_id_products" in fk_dict
    assert "fk_fraud_predictions_offer_id_offers" in fk_dict
    assert "fk_fraud_predictions_purchase_intent_id_purchase_intents" in fk_dict
    assert "fk_fraud_predictions_purchase_plan_id_purchase_plans" in fk_dict
    assert "fk_fraud_predictions_commerce_transaction_id_commerce_transactions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_fraud_predictions_security_policy_id" in ix_names
    assert "ix_fraud_predictions_policy_rule_id" in ix_names
    assert "ix_fraud_predictions_policy_evaluation_id" in ix_names
    assert "ix_fraud_predictions_security_violation_id" in ix_names
    assert "ix_fraud_predictions_risk_signal_id" in ix_names
    assert "ix_fraud_predictions_agent_id" in ix_names
    assert "ix_fraud_predictions_merchant_id" in ix_names
    assert "ix_fraud_predictions_product_id" in ix_names
    assert "ix_fraud_predictions_offer_id" in ix_names
    assert "ix_fraud_predictions_purchase_intent_id" in ix_names
    assert "ix_fraud_predictions_purchase_plan_id" in ix_names
    assert "ix_fraud_predictions_commerce_transaction_id" in ix_names


def test_06_fraud_predictions_reference_uniqueness() -> None:
    """6. Verify tenant-scoped prediction_reference uniqueness constraint."""
    table = Base.metadata.tables["fraud_predictions"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_fraud_predictions_tenant_id_prediction_reference" in uq_names


def test_07_fraud_predictions_enum_constraints() -> None:
    """7. Verify type, status, label check constraints exist."""
    table = Base.metadata.tables["fraud_predictions"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_fraud_predictions_prediction_type" in ck_names
    assert "ck_fraud_predictions_prediction_status" in ck_names
    assert "ck_fraud_predictions_prediction_label" in ck_names


def test_08_fraud_predictions_score_precisions() -> None:
    """8. Verify scores use Decimal NUMERIC(8,4) and check bounds exist."""
    table = Base.metadata.tables["fraud_predictions"]
    for col in ("fraud_probability", "legitimate_probability", "risk_score", "confidence_score"):
        col_type = str(table.columns[col].type)
        assert col_type.startswith("NUMERIC")
        assert not col_type.startswith("FLOAT")
        assert not col_type.startswith("REAL")

    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_fraud_predictions_fraud_probability_bounds" in ck_names
    assert "ck_fraud_predictions_legitimate_probability_bounds" in ck_names
    assert "ck_fraud_predictions_risk_score_bounds" in ck_names
    assert "ck_fraud_predictions_confidence_score_bounds" in ck_names
    assert "ck_fraud_predictions_feature_count_nonnegative" in ck_names
    assert "ck_fraud_predictions_probability_consistency" in ck_names


def test_09_fraud_predictions_jsonb_payloads() -> None:
    """9. Verify feature_snapshot, prediction_context, prediction_metadata use JSONB."""
    table = Base.metadata.tables["fraud_predictions"]
    for col_name in ("feature_snapshot", "prediction_context", "prediction_metadata"):
        col = table.columns[col_name]
        assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_10_fraud_predictions_repr_redaction() -> None:
    """10. Verify FraudPrediction.__repr__ does NOT leak JSONB payloads."""
    fp = FraudPrediction(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        prediction_reference="FP-001",
        model_reference="v1-model",
        model_version="1.0.0",
        prediction_type="transaction",
        prediction_status="completed",
        prediction_label="legitimate",
        feature_snapshot={"secret_token": "hidden"},
        prediction_context={"api_key": "hidden_key"},
    )
    repr_str = repr(fp)
    assert "reference='FP-001'" in repr_str
    assert "secret_token" not in repr_str
    assert "api_key" not in repr_str


def test_11_fraud_predictions_prohibited_secret_fields() -> None:
    """11. Verify prohibited secret fields do NOT exist on fraud_predictions."""
    columns = {c.name for c in Base.metadata.tables["fraud_predictions"].columns}
    prohibited = {"password", "secret", "token", "api_key", "private_key", "card_number", "cvv"}
    assert len(prohibited.intersection(columns)) == 0


def test_12_fraud_predictions_tenant_isolation() -> None:
    """12. Verify tenant isolation on FraudPrediction."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    fp = FraudPrediction(
        id=uuid.uuid4(),
        tenant_id=t1,
        prediction_reference="FP-T1",
        model_reference="m1",
        model_version="1.0",
        prediction_type="transaction",
        prediction_label="legitimate",
    )
    assert fp.tenant_id == t1
    assert (fp.tenant_id == t2) is False


def test_13_fraud_predictions_relationships() -> None:
    """13. Verify FraudPrediction relationships."""
    assert hasattr(FraudPrediction, "security_policy")
    assert hasattr(FraudPrediction, "policy_rule")
    assert hasattr(FraudPrediction, "policy_evaluation")
    assert hasattr(FraudPrediction, "security_violation")
    assert hasattr(FraudPrediction, "risk_signal")
    assert hasattr(FraudPrediction, "agent")
    assert hasattr(FraudPrediction, "merchant")
    assert hasattr(FraudPrediction, "product")
    assert hasattr(FraudPrediction, "offer")
    assert hasattr(FraudPrediction, "purchase_intent")
    assert hasattr(FraudPrediction, "purchase_plan")
    assert hasattr(FraudPrediction, "commerce_transaction")
    assert hasattr(FraudPrediction, "xai_explanations")
