"""ROC-AUC Evaluator Engine (Phase 240)."""

from __future__ import annotations

import logging

from sklearn.metrics import roc_auc_score

from app.schemas.ml_evaluation import RocAucResult

logger = logging.getLogger("fraudguard.ml.evaluation.roc_auc")


class RocAucEvaluator:
    """Production ROC-AUC Evaluator with Single-Class Safety & Probability Integrity (Phase 240)."""

    def evaluate_roc_auc(
        self,
        y_true: list[int],
        y_prob: list[float],
    ) -> RocAucResult:
        """Calculate ROC-AUC score from continuous probabilities (Phase 240)."""
        if len(y_true) != len(y_prob):
            raise ValueError(
                f"Ground truth length ({len(y_true)}) mismatches probability length ({len(y_prob)})"
            )

        pos_count = y_true.count(1)
        neg_count = y_true.count(0)
        sample_count = len(y_true)

        if sample_count == 0:
            return RocAucResult(
                roc_auc=None,
                positive_count=0,
                negative_count=0,
                sample_count=0,
                warning="EMPTY_DATASET",
                explanation="ROC-AUC cannot be calculated on an empty dataset.",
                metric_version="1.0.0",
            )

        # Single-class dataset check: if pos_count == 0 or neg_count == 0, ROC-AUC is undefined
        if pos_count == 0 or neg_count == 0:
            logger.warning(
                "ROC-AUC undefined: Target labels contain single class (positives=%d, negatives=%d)",  # noqa: E501
                pos_count,
                neg_count,
            )
            return RocAucResult(
                roc_auc=None,
                positive_count=pos_count,
                negative_count=neg_count,
                sample_count=sample_count,
                warning="SINGLE_CLASS_TARGET",
                explanation="ROC-AUC is mathematically undefined for single-class target labels.",
                metric_version="1.0.0",
            )

        try:
            auc_raw = float(roc_auc_score(y_true, y_prob))
            score = round(max(0.0, min(1.0, auc_raw)), 6)
            warning = None
        except Exception as exc:
            logger.error("ROC-AUC calculation error: %s", exc)
            score = None
            warning = "CALCULATION_ERROR"

        return RocAucResult(
            roc_auc=score,
            positive_count=pos_count,
            negative_count=neg_count,
            sample_count=sample_count,
            warning=warning,
            explanation="ROC-AUC evaluates ranking performance across all possible decision thresholds.",  # noqa: E501
            metric_version="1.0.0",
        )
