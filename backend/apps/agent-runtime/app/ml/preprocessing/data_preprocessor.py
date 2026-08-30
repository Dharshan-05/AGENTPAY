"""Data Preprocessing Engine (Phase 220)."""

from __future__ import annotations

import logging
import math
from typing import Any

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.schemas.ml_cleaning import PreprocessorState

logger = logging.getLogger("fraudguard.ml.preprocessing")


class DataPreprocessor:
    """Production Preprocessing Pipeline with fit/transform separation (Phase 220)."""

    def __init__(
        self,
        config: MLPipelineConfig | None = None,
        state: PreprocessorState | None = None,
    ) -> None:
        self.config = config or get_default_ml_config()
        self.state = state or PreprocessorState()

    def fit(
        self,
        records: list[dict[str, Any]],
        numerical_columns: list[str],
        categorical_columns: list[str],
        fit_dataset_version: str = "1.0.0",
    ) -> DataPreprocessor:
        """Fit preprocessor state strictly on training records without leakage (Phase 220)."""
        logger.info("Fitting DataPreprocessor on %d records", len(records))

        # 1. Numerical statistics (Mean & Standard Deviation with Numerical Stability)
        means: dict[str, float] = {}
        stds: dict[str, float] = {}

        for col in numerical_columns:
            vals: list[float] = []
            for r in records:
                v = r.get(col)
                if v is not None:
                    try:
                        f_val = float(v)
                        if not math.isnan(f_val) and not math.isinf(f_val):
                            vals.append(f_val)
                    except (ValueError, TypeError):
                        pass
            if vals:
                mean = sum(vals) / len(vals)
                variance = sum((x - mean) ** 2 for x in vals) / max(1, len(vals))
                std = math.sqrt(variance)
                means[col] = mean
                stds[col] = std if std > 1e-6 else 1.0
            else:
                means[col] = 0.0
                stds[col] = 1.0

        # 2. Categorical encodings
        encodings: dict[str, dict[str, int]] = {}
        for col in categorical_columns:
            unique_vals: set[str] = set()
            for r in records:
                v = r.get(col)
                if v is not None:
                    unique_vals.add(str(v))
            col_map = {val: idx + 1 for idx, val in enumerate(sorted(unique_vals))}
            col_map["<UNKNOWN>"] = 0
            encodings[col] = col_map

        self.state = PreprocessorState(
            feature_means=means,
            feature_stds=stds,
            categorical_encodings=encodings,
            imputation_defaults={c: means[c] for c in numerical_columns},
            is_fitted=True,
            preprocessor_version="2.0",
            fit_dataset_version=fit_dataset_version,
            configuration_hash=self.config.compute_configuration_hash(),
        )
        return self

    def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform records using fitted preprocessor state for inference parity (Phase 220)."""  # noqa: E501
        if not self.state.is_fitted:
            raise RuntimeError("DataPreprocessor must be fitted before calling transform()")

        transformed_records: list[dict[str, Any]] = []

        for rec in records:
            t_rec = dict(rec)

            # Transform numerical columns (z-score standardization & NaN/Inf guard)
            for col, mean in self.state.feature_means.items():
                val = rec.get(col)
                std = self.state.feature_stds.get(col, 1.0)
                if val is None:
                    f_val = mean
                else:
                    try:
                        f_val = float(val)
                        if math.isnan(f_val) or math.isinf(f_val):
                            f_val = mean
                    except (ValueError, TypeError):
                        f_val = mean

                scaled_val = (f_val - mean) / std
                t_rec[f"{col}_scaled"] = round(scaled_val, 6)

            # Transform categorical columns (integer encoding with unseen category protection)
            for col, encoding_map in self.state.categorical_encodings.items():
                val = rec.get(col)
                val_str = str(val) if val is not None else "<UNKNOWN>"
                encoded = encoding_map.get(val_str, encoding_map["<UNKNOWN>"])
                t_rec[f"{col}_encoded"] = encoded

            transformed_records.append(t_rec)

        return transformed_records

    def fit_transform(
        self,
        records: list[dict[str, Any]],
        numerical_columns: list[str],
        categorical_columns: list[str],
        fit_dataset_version: str = "1.0.0",
    ) -> list[dict[str, Any]]:
        """Fit and transform in a single call."""
        self.fit(records, numerical_columns, categorical_columns, fit_dataset_version)
        return self.transform(records)
