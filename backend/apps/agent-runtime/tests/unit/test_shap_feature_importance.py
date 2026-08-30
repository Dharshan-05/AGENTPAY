"""Unit tests for SHAP Feature Importance Service (Phase 257)."""

from __future__ import annotations

import uuid

from app.ml.xai.feature_importance import ShapFeatureImportanceService
from app.schemas.ml_xai import ShapAttributionResult


def test_01_valid_feature_importance_calculation_and_ranking() -> None:
    """1. Test feature importance calculation, direction mapping, relative normalization, and deterministic ranking."""  # noqa: E501
    service = ShapFeatureImportanceService()

    attr_res = ShapAttributionResult(
        explanation_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        model_name="m1",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        feature_names=["feat_a", "feat_b", "feat_c"],
        feature_versions={"feat_a": "1.0.0", "feat_b": "1.0.0", "feat_c": "1.0.0"},
        shap_values=[0.40, -0.60, 0.0],
        base_value=0.10,
        prediction_probability=0.30,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    importances = service.compute_feature_importance(attr_res)

    assert len(importances) == 3
    # Rank 1: feat_b (abs = 0.60, direction NEGATIVE)
    assert importances[0].feature_name == "feat_b"
    assert importances[0].rank == 1
    assert importances[0].direction == "NEGATIVE"
    assert importances[0].relative_importance == 0.60  # 0.6 / (0.4 + 0.6)

    # Rank 2: feat_a (abs = 0.40, direction POSITIVE)
    assert importances[1].feature_name == "feat_a"
    assert importances[1].rank == 2
    assert importances[1].direction == "POSITIVE"

    # Rank 3: feat_c (abs = 0.0, direction NEUTRAL)
    assert importances[2].feature_name == "feat_c"
    assert importances[2].rank == 3
    assert importances[2].direction == "NEUTRAL"


def test_02_zero_denominator_handled_safely() -> None:
    """2. Test that zero SHAP sum is handled safely with 0.0 relative importance and zero crashes."""  # noqa: E501
    service = ShapFeatureImportanceService()

    attr_zero = ShapAttributionResult(
        explanation_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        model_name="m1",
        model_version="1.0.0",
        artifact_checksum="a" * 64,
        feature_names=["feat_a", "feat_b"],
        feature_versions={},
        shap_values=[0.0, 0.0],
        base_value=0.0,
        prediction_probability=0.5,
        configuration_hash="c" * 64,
        result_fingerprint="r" * 64,
    )

    importances = service.compute_feature_importance(attr_zero)
    assert importances[0].relative_importance == 0.0
    assert importances[1].relative_importance == 0.0
