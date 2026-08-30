"""SHAP Feature Importance Service (Phase 257)."""

from __future__ import annotations

import logging
from typing import Any

from app.schemas.ml_xai import ShapAttributionResult, ShapFeatureImportance

logger = logging.getLogger("fraudguard.ml.xai.importance")


class ShapFeatureImportanceService:
    """Production SHAP Feature Importance Service (Phase 257)."""

    def compute_feature_importance(
        self,
        attribution_result: ShapAttributionResult,
    ) -> list[ShapFeatureImportance]:
        """Convert raw SHAP attribution values into normalized, ranked feature importances (Phase 257)."""  # noqa: E501
        logger.info(
            "Computing feature importance for explanation %s (features=%d)",
            attribution_result.explanation_id,
            len(attribution_result.feature_names),
        )

        names = attribution_result.feature_names
        vals = attribution_result.shap_values
        versions = attribution_result.feature_versions

        if len(names) != len(vals):
            raise ValueError(
                f"Feature names count ({len(names)}) mismatches SHAP values count ({len(vals)})"
            )  # noqa: E501

        abs_vals = [abs(v) for v in vals]
        sum_abs = sum(abs_vals)

        items: list[dict[str, Any]] = []
        for name, val in zip(names, vals, strict=True):
            abs_imp = round(abs(val), 6)
            rel_imp = min(1.0, max(0.0, round(abs_imp / sum_abs, 6))) if sum_abs > 0 else 0.0

            if val > 0:
                direction = "POSITIVE"
            elif val < 0:
                direction = "NEGATIVE"
            else:
                direction = "NEUTRAL"

            ver = versions.get(name, "1.0.0")
            items.append(
                {
                    "feature_name": name,
                    "feature_version": ver,
                    "shap_value": val,
                    "absolute_importance": abs_imp,
                    "relative_importance": rel_imp,
                    "direction": direction,
                }
            )

        # Deterministic sorting: 1. absolute_importance descending, 2. feature_name ascending
        items.sort(key=lambda x: (-x["absolute_importance"], x["feature_name"]))

        importances: list[ShapFeatureImportance] = []
        for rank_idx, item in enumerate(items, start=1):
            importances.append(
                ShapFeatureImportance(
                    feature_name=item["feature_name"],
                    feature_version=item["feature_version"],
                    shap_value=item["shap_value"],
                    absolute_importance=item["absolute_importance"],
                    relative_importance=item["relative_importance"],
                    direction=item["direction"],
                    rank=rank_idx,
                )
            )

        return importances
