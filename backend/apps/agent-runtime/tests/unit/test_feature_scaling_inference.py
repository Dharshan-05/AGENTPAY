"""Unit tests for Feature Scaling in Inference (Phase 247)."""

from __future__ import annotations

import pytest

from app.ml.inference.scaling import InferenceScaler
from app.schemas.ml_cleaning import PreprocessorState


def test_01_scaling_with_frozen_state_and_no_refit() -> None:
    """1. Test feature scaling using frozen PreprocessorState without refitting."""
    state = PreprocessorState(
        feature_means={"amount": 100.0, "risk_score": 0.50},
        feature_stds={"amount": 20.0, "risk_score": 0.10},
        is_fitted=True,
    )

    scaler = InferenceScaler(state=state)

    # Transform feature dict: (120 - 100) / 20 = 1.0; (0.60 - 0.50) / 0.10 = 1.0
    scaled = scaler.scale_features({"amount": 120.0, "risk_score": 0.60})
    assert scaled["amount"] == 1.0
    assert scaled["risk_score"] == 1.0

    # Ensure no fit method exists on InferenceScaler!
    assert not hasattr(scaler, "fit")


def test_02_unfitted_or_missing_state_fails_closed() -> None:
    """2. Mandatory Test: Unfitted or missing PreprocessorState must fail closed."""
    with pytest.raises(ValueError, match="PreprocessorState is missing or not fitted!"):
        InferenceScaler(state=None)

    unfitted_state = PreprocessorState(is_fitted=False)
    with pytest.raises(ValueError, match="PreprocessorState is missing or not fitted!"):
        InferenceScaler(state=unfitted_state)


def test_03_nan_inf_rejection_in_scaler() -> None:
    """3. Test rejection of NaN and Infinity values in feature scaler."""
    state = PreprocessorState(
        feature_means={"amount": 100.0}, feature_stds={"amount": 20.0}, is_fitted=True
    )  # noqa: E501
    scaler = InferenceScaler(state=state)

    with pytest.raises(ValueError, match="contains NaN or Infinity"):
        scaler.scale_features({"amount": float("nan")})

    with pytest.raises(ValueError, match="contains NaN or Infinity"):
        scaler.scale_features({"amount": float("inf")})
