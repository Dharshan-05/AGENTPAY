"""Hyperparameter Search Space Definition (Phase 235)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class HyperparameterSearchSpace:
    """Strongly typed hyperparameter search space bounds and candidate generator (Phase 235)."""

    max_depth_options: list[int] = field(default_factory=lambda: [3, 5, 7])
    learning_rate_options: list[float] = field(default_factory=lambda: [0.01, 0.05, 0.1])
    n_estimators_options: list[int] = field(default_factory=lambda: [50, 100, 150])
    subsample_options: list[float] = field(default_factory=lambda: [0.7, 0.9])
    colsample_bytree_options: list[float] = field(default_factory=lambda: [0.7, 0.9])
    min_child_weight_options: list[float] = field(default_factory=lambda: [1.0, 3.0])
    scale_pos_weight_options: list[float] = field(default_factory=lambda: [1.0, 5.0])

    def to_summary_dict(self) -> dict[str, Any]:
        """Summary representation of search space bounds."""
        return {
            "max_depth_options": self.max_depth_options,
            "learning_rate_options": self.learning_rate_options,
            "n_estimators_options": self.n_estimators_options,
            "subsample_options": self.subsample_options,
            "colsample_bytree_options": self.colsample_bytree_options,
            "min_child_weight_options": self.min_child_weight_options,
            "scale_pos_weight_options": self.scale_pos_weight_options,
        }
