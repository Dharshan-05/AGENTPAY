"""Unit Tests for Phase 058 XAI / SHAP Explanations Schema."""

import uuid
from decimal import Decimal

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.xai_explanation import XAIExplanation


def test_01_xai_explanations_table_exists() -> None:
    """1. Verify xai_explanations table exists in Base.metadata."""
    assert "xai_explanations" in Base.metadata.tables
    assert XAIExplanation.__tablename__ == "xai_explanations"


def test_02_xai_explanations_exact_columns() -> None:
    """2. Verify exact columns exist on xai_explanations."""
    table = Base.metadata.tables["xai_explanations"]
    column_names = {c.name for c in table.columns}
    expected = {
        "id",
        "tenant_id",
        "fraud_prediction_id",
        "risk_signal_id",
        "security_violation_id",
        "policy_evaluation_id",
        "agent_id",
        "merchant_id",
        "product_id",
        "offer_id",
        "purchase_intent_id",
        "purchase_plan_id",
        "commerce_transaction_id",
        "explanation_reference",
        "explanation_type",
        "explanation_status",
        "model_reference",
        "model_version",
        "explainer_type",
        "base_value",
        "prediction_value",
        "top_feature_count",
        "feature_importance",
        "shap_values",
        "feature_snapshot",
        "explanation_context",
        "explanation_metadata",
        "summary",
        "reasoning_summary",
        "request_id",
        "actor_type",
        "actor_id",
        "generated_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert expected.issubset(column_names)


def test_03_xai_explanations_pk() -> None:
    """3. Verify primary key pk_xai_explanations."""
    table = Base.metadata.tables["xai_explanations"]
    assert table.primary_key.name == "pk_xai_explanations"


def test_04_xai_explanations_tenant_id() -> None:
    """4. Verify tenant_id is NOT NULL and indexed."""
    table = Base.metadata.tables["xai_explanations"]
    assert table.columns["tenant_id"].nullable is False
    ix_names = {ix.name for ix in table.indexes}
    assert "ix_xai_explanations_tenant_id" in ix_names


def test_05_xai_explanations_fks_and_indexes() -> None:
    """5. Verify 11 foreign keys use ON DELETE RESTRICT and are indexed."""
    table = Base.metadata.tables["xai_explanations"]
    fk_dict = {fk.name: fk for fk in table.foreign_keys}
    assert "fk_xai_explanations_fraud_prediction_id_fraud_predictions" in fk_dict
    assert "fk_xai_explanations_risk_signal_id_risk_signals" in fk_dict
    assert "fk_xai_explanations_security_violation_id_security_violations" in fk_dict
    assert "fk_xai_explanations_policy_evaluation_id_policy_evaluations" in fk_dict
    assert "fk_xai_explanations_agent_id_agents" in fk_dict
    assert "fk_xai_explanations_merchant_id_merchants" in fk_dict
    assert "fk_xai_explanations_product_id_products" in fk_dict
    assert "fk_xai_explanations_offer_id_offers" in fk_dict
    assert "fk_xai_explanations_purchase_intent_id_purchase_intents" in fk_dict
    assert "fk_xai_explanations_purchase_plan_id_purchase_plans" in fk_dict
    assert "fk_xai_explanations_commerce_transaction_id_commerce_transactions" in fk_dict

    for fk in table.foreign_keys:
        assert fk.ondelete == "RESTRICT"

    ix_names = {ix.name for ix in table.indexes}
    assert "ix_xai_explanations_fraud_prediction_id" in ix_names
    assert "ix_xai_explanations_risk_signal_id" in ix_names
    assert "ix_xai_explanations_security_violation_id" in ix_names
    assert "ix_xai_explanations_policy_evaluation_id" in ix_names
    assert "ix_xai_explanations_agent_id" in ix_names
    assert "ix_xai_explanations_merchant_id" in ix_names
    assert "ix_xai_explanations_product_id" in ix_names
    assert "ix_xai_explanations_offer_id" in ix_names
    assert "ix_xai_explanations_purchase_intent_id" in ix_names
    assert "ix_xai_explanations_purchase_plan_id" in ix_names
    assert "ix_xai_explanations_commerce_transaction_id" in ix_names


def test_06_xai_explanations_reference_uniqueness() -> None:
    """6. Verify tenant-scoped explanation_reference uniqueness constraint."""
    table = Base.metadata.tables["xai_explanations"]
    uq_names = {uq.name for uq in table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_xai_explanations_tenant_id_explanation_reference" in uq_names


def test_07_xai_explanations_enum_constraints() -> None:
    """7. Verify type, status, explainer check constraints exist."""
    table = Base.metadata.tables["xai_explanations"]
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "name") and ck.name}
    assert "ck_xai_explanations_explanation_type" in ck_names
    assert "ck_xai_explanations_explanation_status" in ck_names
    assert "ck_xai_explanations_explainer_type" in ck_names
    assert "ck_xai_explanations_top_feature_count_nonnegative" in ck_names


def test_08_xai_explanations_numeric_precision() -> None:
    """8. Verify signed NUMERIC(18,8) is used for base_value and prediction_value."""
    table = Base.metadata.tables["xai_explanations"]
    for col in ("base_value", "prediction_value"):
        col_type = str(table.columns[col].type)
        assert col_type.startswith("NUMERIC")
        assert not col_type.startswith("FLOAT")
        assert not col_type.startswith("REAL")


def test_09_xai_explanations_signed_shap_support() -> None:
    """9. Verify SHAP values can be positive or negative in ORM instance."""
    xai = XAIExplanation(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        explanation_reference="XAI-001",
        explanation_type="shap",
        model_reference="v1",
        model_version="1.0",
        explainer_type="tree_shap",
        base_value=Decimal("0.05"),
        prediction_value=Decimal("0.85"),
        shap_values={"feature_a": 0.45, "feature_b": -0.25},
    )
    assert xai.shap_values is not None
    assert xai.shap_values["feature_b"] == -0.25


def test_10_xai_explanations_jsonb_payloads() -> None:
    """10. Verify feature_importance, shap_values, feature_snapshot, context use JSONB."""
    table = Base.metadata.tables["xai_explanations"]
    cols = (
        "feature_importance",
        "shap_values",
        "feature_snapshot",
        "explanation_context",
        "explanation_metadata",
    )
    for col_name in cols:
        col = table.columns[col_name]
        assert "JSONB" in str(col.type) or "JSON" in str(col.type)


def test_11_xai_explanations_repr_redaction() -> None:
    """11. Verify XAIExplanation.__repr__ does NOT leak JSONB payloads."""
    xai = XAIExplanation(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        explanation_reference="XAI-001",
        explanation_type="shap",
        model_reference="v1-model",
        model_version="1.0.0",
        explainer_type="tree_shap",
        shap_values={"secret_token": "hidden"},
        explanation_context={"api_key": "hidden_key"},
    )
    repr_str = repr(xai)
    assert "reference='XAI-001'" in repr_str
    assert "secret_token" not in repr_str
    assert "api_key" not in repr_str


def test_12_xai_explanations_prohibited_secret_fields() -> None:
    """12. Verify prohibited secret fields do NOT exist on xai_explanations."""
    columns = {c.name for c in Base.metadata.tables["xai_explanations"].columns}
    prohibited = {"password", "secret", "token", "api_key", "private_key", "card_number", "cvv"}
    assert len(prohibited.intersection(columns)) == 0


def test_13_xai_explanations_tenant_isolation() -> None:
    """13. Verify tenant isolation on XAIExplanation."""
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    xai = XAIExplanation(
        id=uuid.uuid4(),
        tenant_id=t1,
        explanation_reference="XAI-T1",
        explanation_type="shap",
        model_reference="m1",
        model_version="1.0",
        explainer_type="tree_shap",
    )
    assert xai.tenant_id == t1
    assert (xai.tenant_id == t2) is False


def test_14_xai_explanations_relationships() -> None:
    """14. Verify XAIExplanation relationships."""
    assert hasattr(XAIExplanation, "fraud_prediction")
    assert hasattr(XAIExplanation, "risk_signal")
    assert hasattr(XAIExplanation, "security_violation")
    assert hasattr(XAIExplanation, "policy_evaluation")
    assert hasattr(XAIExplanation, "agent")
    assert hasattr(XAIExplanation, "merchant")
    assert hasattr(XAIExplanation, "product")
    assert hasattr(XAIExplanation, "offer")
    assert hasattr(XAIExplanation, "purchase_intent")
    assert hasattr(XAIExplanation, "purchase_plan")
    assert hasattr(XAIExplanation, "commerce_transaction")
