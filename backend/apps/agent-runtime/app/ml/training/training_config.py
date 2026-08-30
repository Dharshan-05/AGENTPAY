"""XGBoost Training Configuration Specifications (Phase 234)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class XGBoostTrainingConfig:
    """Strongly typed configuration for XGBoost model training (Phase 234)."""

    objective: str = "binary:logistic"
    eval_metric: str = "logloss"
    n_estimators: int = 100
    max_depth: int = 6
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    min_child_weight: float = 1.0
    gamma: float = 0.0
    reg_alpha: float = 0.0
    reg_lambda: float = 1.0
    random_state: int = 42
    n_jobs: int = -1
    scale_pos_weight: float = 1.0
    early_stopping_rounds: int | None = 10
    tree_method: str = "auto"
    extra_params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate hyperparameter range boundaries."""
        if self.n_estimators <= 0:
            raise ValueError(f"n_estimators must be > 0 (got {self.n_estimators})")
        if self.max_depth <= 0:
            raise ValueError(f"max_depth must be > 0 (got {self.max_depth})")
        if not (0.0 < self.learning_rate <= 1.0):
            raise ValueError(f"learning_rate must be in (0.0, 1.0] (got {self.learning_rate})")
        if not (0.0 < self.subsample <= 1.0):
            raise ValueError(f"subsample must be in (0.0, 1.0] (got {self.subsample})")
        if not (0.0 < self.colsample_bytree <= 1.0):
            raise ValueError(
                f"colsample_bytree must be in (0.0, 1.0] (got {self.colsample_bytree})"
            )  # noqa: E501

    def to_xgb_params(self) -> dict[str, Any]:
        """Convert config to dictionary parameters compatible with XGBClassifier."""
        params = {
            "objective": self.objective,
            "eval_metric": self.eval_metric,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "learning_rate": self.learning_rate,
            "subsample": self.subsample,
            "colsample_bytree": self.colsample_bytree,
            "min_child_weight": self.min_child_weight,
            "gamma": self.gamma,
            "reg_alpha": self.reg_alpha,
            "reg_lambda": self.reg_lambda,
            "random_state": self.random_state,
            "n_jobs": self.n_jobs,
            "scale_pos_weight": self.scale_pos_weight,
            "tree_method": self.tree_method,
        }
        if self.early_stopping_rounds is not None and self.early_stopping_rounds > 0:
            params["early_stopping_rounds"] = self.early_stopping_rounds

        params.update(self.extra_params)
        return params

    def compute_configuration_hash(self) -> str:
        """Compute SHA-256 hash of training parameters for reproducibility identity."""
        params_dict = self.to_xgb_params()
        encoded = json.dumps(params_dict, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
