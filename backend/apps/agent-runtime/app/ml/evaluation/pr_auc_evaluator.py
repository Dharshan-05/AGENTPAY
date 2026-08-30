"""PR-AUC / Average Precision Evaluator Engine (Phase 241)."""

from __future__ import annotations

import logging

from sklearn.metrics import average_precision_score

from app.schemas.ml_evaluation import PrAucResult

logger = logging.getLogger("fraudguard.ml.evaluation.pr_auc")


class PrAucEvaluator:
    """Production Precision-Recall AUC (Average Precision) Evaluator with Bounds Verification (Phase 241)."""  # noqa: E501

    def evaluate_pr_auc(
        self,
        y_true: list[int],
        y_prob: list[float],
    ) -> PrAucResult:
        """Calculate Precision-Recall AUC using Average Precision from continuous probabilities (Phase 241)."""  # noqa: E501
        if len(y_true) != len(y_prob):
            raise ValueError(
                f"Ground truth length ({len(y_true)}) mismatches probability length ({len(y_prob)})"
            )

        pos_count = y_true.count(1)
        neg_count = y_true.count(0)
        sample_count = len(y_true)

        if sample_count == 0:
            return PrAucResult(
                pr_auc=None,
                positive_count=0,
                negative_count=0,
                sample_count=0,
                warning="EMPTY_DATASET",
                explanation="PR-AUC cannot be calculated on an empty dataset.",
                metric_definition="AVERAGE_PRECISION",
                metric_version="1.0.0",
            )

        if pos_count == 0:
            logger.warning("PR-AUC undefined: Target labels contain no positive fraud instances.")
            return PrAucResult(
                pr_auc=None,
                positive_count=0,
                negative_count=neg_count,
                sample_count=sample_count,
                warning="NO_POSITIVE_GROUND_TRUTH",
                explanation="PR-AUC / Average Precision is undefined without ground truth positive instances.",  # noqa: E501
                metric_definition="AVERAGE_PRECISION",
                metric_version="1.0.0",
            )

        try:
            ap_raw = float(average_precision_score(y_true, y_prob))
            score = round(max(0.0, min(1.0, ap_raw)), 6)
            warning = None
        except Exception as exc:
            logger.error("PR-AUC calculation error: %s", exc)
            score = None
            warning = "CALCULATION_ERROR"

        return PrAucResult(
            pr_auc=score,
            positive_count=pos_count,
            negative_count=neg_count,
            sample_count=sample_count,
            warning=warning,
            explanation="PR-AUC evaluates precision-recall curve performance via Average Precision.",  # noqa: E501
            metric_definition="AVERAGE_PRECISION",
            metric_version="1.0.0",
        )
