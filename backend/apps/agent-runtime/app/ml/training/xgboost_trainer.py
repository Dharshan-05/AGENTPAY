"""XGBoost Training Engine Implementation (Phase 234)."""

from __future__ import annotations

import logging
import math
import time
import uuid
from decimal import Decimal
from typing import Any

import numpy as np
import xgboost as xgb

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.splitting.dataset_splitter import DatasetSplits
from app.ml.training.training_config import XGBoostTrainingConfig
from app.schemas.ml_training import ModelTrainingResult

logger = logging.getLogger("fraudguard.ml.training")


class XGBoostTrainer:
    """Production XGBoost Model Training Engine (Phase 234)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()

    def _convert_to_matrix(
        self, X_dicts: list[dict[str, Any]], expected_feature_names: list[str]
    ) -> Any:
        """Convert list of feature dicts to 2D numpy float32 matrix using strict feature order (Phase 234.10)."""  # noqa: E501
        if not X_dicts:
            raise ValueError("Feature record matrix is empty.")

        metadata_keys = {"transaction_id", "tenant_id", "agent_id", "created_at"}
        valid_feature_names = [f for f in expected_feature_names if f not in metadata_keys]

        n_rows = len(X_dicts)
        n_cols = len(valid_feature_names)
        matrix = np.zeros((n_rows, n_cols), dtype=np.float32)

        for i, row in enumerate(X_dicts):
            for j, f_name in enumerate(valid_feature_names):
                val = row.get(f_name)
                if val is None:
                    raise ValueError(f"Feature '{f_name}' at row {i} is None/missing.")

                # Handle Decimal, boolean, and numerical types safely
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
                        raise ValueError(
                            f"Feature '{f_name}' at row {i} has unparseable value '{val}'"
                        ) from exc

                # Numerical Safety Check (NaN / Inf)
                if math.isnan(f_val) or math.isinf(f_val):
                    raise ValueError(
                        f"Numerical safety error: Feature '{f_name}' at row {i} contains NaN/Inf ({f_val})"  # noqa: E501
                    )

                matrix[i, j] = f_val

        return matrix

    def train(
        self,
        splits: DatasetSplits,
        training_config: XGBoostTrainingConfig | None = None,
        feature_order: list[str] | None = None,
    ) -> tuple[xgb.XGBClassifier, ModelTrainingResult]:
        """Train XGBoost model on train split, evaluate on validation split (Phase 234)."""
        t_start = time.time()
        cfg = training_config or XGBoostTrainingConfig(random_state=self.config.random_seed)

        # 1. Validation & Test Isolation Protection
        train_ds = splits.train_dataset
        val_ds = splits.validation_dataset
        test_ds = splits.test_dataset

        # Explicit Test Set Isolation Assertion
        if test_ds is None:
            raise ValueError("Invalid DatasetSplits object.")
            raise ValueError("Training dataset partitions cannot be empty.")

        # Single class check
        unique_train_labels = set(train_ds.y)
        if len(unique_train_labels) < 2:
            raise ValueError(
                f"Training dataset must contain both 0 and 1 class labels (got {unique_train_labels})."  # noqa: E501
            )

        # Determine feature names and enforce feature order integrity
        expected_features = feature_order or train_ds.feature_names
        if feature_order and feature_order != train_ds.feature_names:
            if set(feature_order) != set(train_ds.feature_names):
                raise ValueError(
                    "Feature order mismatch: supplied feature order does not match dataset features!"  # noqa: E501
                )

        # 2. Convert Data to Numeric Numpy Matrices with strict order integrity
        X_train_mat = self._convert_to_matrix(train_ds.X, expected_features)
        y_train_arr = np.array(train_ds.y, dtype=np.int32)

        X_val_mat = self._convert_to_matrix(val_ds.X, expected_features) if val_ds.X else None
        y_val_arr = np.array(val_ds.y, dtype=np.int32) if val_ds.y else None

        # 3. Configure XGBClassifier
        params = cfg.to_xgb_params()
        eval_set = (
            [(X_val_mat, y_val_arr)]
            if (X_val_mat is not None and y_val_arr is not None and len(X_val_mat) > 0)
            else None
        )
        if not eval_set and "early_stopping_rounds" in params:
            del params["early_stopping_rounds"]

        model = xgb.XGBClassifier(**params)

        # 4. Execute Fit
        logger.info(
            "Executing XGBoost training on %d samples (features=%d)",
            len(y_train_arr),
            len(expected_features),
        )  # noqa: E501
        if eval_set:
            model.fit(
                X_train_mat,
                y_train_arr,
                eval_set=eval_set,
                verbose=False,
            )
        else:
            model.fit(X_train_mat, y_train_arr, verbose=False)

        duration = round(time.time() - t_start, 4)

        # Extract Early Stopping Metrics
        best_iter = getattr(model, "best_iteration", None)
        best_score = (
            float(getattr(model, "best_score", 0.0)) if hasattr(model, "best_score") else None
        )  # noqa: E501

        run_id = uuid.uuid4()
        result = ModelTrainingResult(
            training_run_id=run_id,
            model_type="XGBoost",
            algorithm="XGBClassifier",
            dataset_fingerprint=train_ds.manifest.dataset_fingerprint,
            feature_count=len(expected_features),
            feature_names=expected_features,
            feature_versions=train_ds.manifest.feature_versions,
            training_rows=len(y_train_arr),
            validation_rows=len(y_val_arr) if y_val_arr is not None else 0,
            hyperparameters=cfg.to_xgb_params(),
            random_seed=cfg.random_state,
            early_stopping_enabled=cfg.early_stopping_rounds is not None,
            best_iteration=best_iter,
            best_score=best_score,
            training_duration_seconds=duration,
            status="SUCCEEDED",
            warnings=[],
        )

        logger.info(
            "XGBoost training succeeded (Run ID: %s, duration: %.2fs, best_score: %s)",
            run_id,
            duration,
            best_score,
        )

        return model, result
