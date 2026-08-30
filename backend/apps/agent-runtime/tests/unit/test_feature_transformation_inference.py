"""Unit and Adversarial Tests for Feature Transformation (Phase 248)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.ml.inference.transformation import InferenceFeatureTransformer
from app.schemas.ml_inference import InferenceRequest


def test_01_valid_feature_transformation_and_ordering() -> None:
    """1. Test valid feature transformation, Decimal handling, and column order binding."""
    transformer = InferenceFeatureTransformer()

    req = InferenceRequest(
        tenant_id=uuid.uuid4(),
        transaction_id="tx_001",
        feature_values={
            "feat_b": Decimal("200.50"),
            "feat_a": 100.0,
            "feat_c": True,
        },
    )

    # Expected feature order: ["feat_a", "feat_b", "feat_c"]
    matrix = transformer.transform_request(
        req, expected_feature_names=["feat_a", "feat_b", "feat_c"]
    )  # noqa: E501

    assert matrix.shape == (1, 3)
    assert matrix[0, 0] == 100.0
    assert matrix[0, 1] == 200.50
    assert matrix[0, 2] == 1.0


def test_02_mandatory_point_in_time_future_timestamp_rejection() -> None:
    """2. Mandatory Adversarial Test: Future feature timestamp must raise Point-in-Time violation."""  # noqa: E501
    transformer = InferenceFeatureTransformer()
    now = datetime.now(UTC)
    future_time = now + timedelta(hours=2)

    req = InferenceRequest(
        tenant_id=uuid.uuid4(),
        transaction_id="tx_002",
        prediction_timestamp=now,
        feature_values={"amount": 100.0},
        feature_timestamps={"amount": future_time},
    )

    with pytest.raises(
        ValueError, match="Point-in-time violation: feature 'amount' timestamp is in the future!"
    ):  # noqa: E501
        transformer.transform_request(req, expected_feature_names=["amount"])


def test_03_missing_feature_and_nan_rejection() -> None:
    """3. Test missing feature rejection and NaN/Inf rejection during transformation."""
    transformer = InferenceFeatureTransformer()

    req_missing = InferenceRequest(
        tenant_id=uuid.uuid4(),
        transaction_id="tx_003",
        feature_values={"feat_a": 10.0},
    )

    with pytest.raises(ValueError, match="Inference request missing required model features"):
        transformer.transform_request(req_missing, expected_feature_names=["feat_a", "feat_b"])

    req_nan = InferenceRequest(
        tenant_id=uuid.uuid4(),
        transaction_id="tx_004",
        feature_values={"feat_a": float("nan")},
    )

    with pytest.raises(
        ValueError, match="Numerical safety error: feature 'feat_a' contains NaN/Inf"
    ):  # noqa: E501
        transformer.transform_request(req_nan, expected_feature_names=["feat_a"])
