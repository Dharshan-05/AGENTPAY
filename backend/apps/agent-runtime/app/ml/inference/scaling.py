"""Production Feature Scaling for Inference (Phase 247)."""

from __future__ import annotations

import logging
import math
from typing import Any

from app.schemas.ml_cleaning import PreprocessorState

logger = logging.getLogger("fraudguard.ml.inference.scaling")


class InferenceScaler:
    """Production Inference Feature Scaler with Frozen PreprocessorState (Phase 247)."""

    def __init__(self, state: PreprocessorState | None = None) -> None:
        if state is None or not state.is_fitted:
            logger.error(
                "InferenceScaler initialization failed: PreprocessorState missing or unfitted!"
            )  # noqa: E501
            raise ValueError(
                "PreprocessorState is missing or not fitted! Refitting scaler during inference is strictly forbidden!"  # noqa: E501
            )
        self.state = state

    def scale_features(self, feature_dict: dict[str, Any]) -> dict[str, Any]:
        """Transform inference features using frozen training PreprocessorState (Phase 247)."""
        scaled: dict[str, Any] = dict(feature_dict)

        for col, mean in self.state.feature_means.items():
            val = feature_dict.get(col)
            std = self.state.feature_stds.get(col, 1.0)

            if val is None:
                f_val = mean
            else:
                try:
                    f_val = float(val)
                except (ValueError, TypeError) as exc:
                    raise ValueError(
                        f"Feature '{col}' value '{val}' cannot be converted to float."
                    ) from exc  # noqa: E501

            if math.isnan(f_val) or math.isinf(f_val):
                raise ValueError(f"Feature '{col}' contains NaN or Infinity ({f_val}).")

            # Z-score standardization: (x - mean) / std
            z_score = (f_val - mean) / (std if std > 1e-6 else 1.0)

            # Numerical safety check (overflow/underflow guard)
            if math.isnan(z_score) or math.isinf(z_score):
                raise ValueError(f"Scaled feature '{col}' resulted in NaN/Inf ({z_score}).")

            scaled[col] = round(z_score, 6)

        return scaled
