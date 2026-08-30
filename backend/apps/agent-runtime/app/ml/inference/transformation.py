"""Production Feature Transformation Pipeline for Inference (Phase 248)."""

from __future__ import annotations

import logging
import math
from datetime import UTC
from decimal import Decimal
from typing import Any

import numpy as np

from app.ml.inference.scaling import InferenceScaler
from app.schemas.ml_inference import InferenceRequest

logger = logging.getLogger("fraudguard.ml.inference.transformation")


class InferenceFeatureTransformer:
    """Production Feature Transformer enforcing Point-in-Time Correctness & Model Contract (Phase 248)."""  # noqa: E501

    def __init__(self, scaler: InferenceScaler | None = None) -> None:
        self.scaler = scaler

    def transform_request(
        self,
        request: InferenceRequest,
        expected_feature_names: list[str],
        expected_feature_versions: dict[str, str] | None = None,
    ) -> np.ndarray[Any, Any]:
        """Transform raw inference request into validated, point-in-time numeric feature matrix (Phase 248)."""  # noqa: E501
        logger.info(
            "Transforming inference request for transaction %s (tenant=%s)",
            request.transaction_id,
            request.tenant_id,
        )

        pred_time = (
            request.prediction_timestamp.replace(tzinfo=UTC)
            if request.prediction_timestamp.tzinfo is None
            else request.prediction_timestamp
        )  # noqa: E501

        # 1. Point-in-Time Validation
        for feat_name, feat_ts in request.feature_timestamps.items():
            f_time = feat_ts.replace(tzinfo=UTC) if feat_ts.tzinfo is None else feat_ts
            if f_time > pred_time:
                logger.error(
                    "Point-in-time violation: feature '%s' timestamp (%s) > prediction_timestamp (%s)",  # noqa: E501
                    feat_name,
                    f_time,
                    pred_time,
                )
                raise ValueError(
                    f"Point-in-time violation: feature '{feat_name}' timestamp is in the future!"
                )

        # 2. Feature Version Integrity Check
        if expected_feature_versions and request.required_feature_versions:
            for f_name, req_ver in request.required_feature_versions.items():
                exp_ver = expected_feature_versions.get(f_name)
                if exp_ver and req_ver != exp_ver:
                    raise ValueError(
                        f"Feature version mismatch for '{f_name}': model expects version '{exp_ver}', request specified '{req_ver}'"  # noqa: E501
                    )

        # 3. Missing Feature Rejection & Feature Contract Validation
        raw_values = dict(request.feature_values)
        missing_features = set(expected_feature_names) - set(raw_values.keys())
        if missing_features:
            raise ValueError(
                f"Inference request missing required model features: {sorted(list(missing_features))}"  # noqa: E501
            )

        # 4. Optional Preprocessing / Scaling using frozen scaler
        processed_values = self.scaler.scale_features(raw_values) if self.scaler else raw_values

        # 5. Numerical Safety & Safe Matrix Construction in exact model feature order
        n_cols = len(expected_feature_names)
        matrix = np.zeros((1, n_cols), dtype=np.float32)

        for j, f_name in enumerate(expected_feature_names):
            val = processed_values.get(f_name)
            if val is None:
                raise ValueError(f"Feature '{f_name}' value is None.")

            # Safe Decimal & numeric conversion
            if isinstance(val, Decimal):
                f_val = float(val)
            elif isinstance(val, bool):
                f_val = 1.0 if val else 0.0
            elif isinstance(val, (int, float)):
                f_val = float(val)
            else:
                try:
                    f_val = float(val)
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"Feature '{f_name}' has unparseable value '{val}'") from exc

            # Rejection of NaN & Infinity
            if math.isnan(f_val) or math.isinf(f_val):
                raise ValueError(
                    f"Numerical safety error: feature '{f_name}' contains NaN/Inf ({f_val})"
                )  # noqa: E501

            matrix[0, j] = f_val

        return matrix
