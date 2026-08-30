"""Precision Evaluator Engine (Phase 237)."""

from __future__ import annotations

import logging

from app.schemas.ml_evaluation import PrecisionResult

logger = logging.getLogger("fraudguard.ml.evaluation.precision")


class PrecisionEvaluator:
    """Production Precision Evaluator with Zero-Division Safety & Bounds Verification (Phase 237)."""  # noqa: E501

    def evaluate_precision(
        self,
        y_true: list[int],
        y_pred: list[int],
        threshold: float = 0.50,
    ) -> PrecisionResult:
        """Calculate precision score TP / (TP + FP) with zero-division protection (Phase 237)."""
        if len(y_true) != len(y_pred):
            raise ValueError(
                f"Ground truth length ({len(y_true)}) mismatches prediction length ({len(y_pred)})"
            )

        tp = 0
        fp = 0

        for true_val, pred_val in zip(y_true, y_pred, strict=True):
            if pred_val == 1:
                if true_val == 1:
                    tp += 1
                else:
                    fp += 1

        support = tp + fp

        if support == 0:
            logger.warning(
                "Precision zero-division: No positive predictions made at threshold %.2f", threshold
            )
            return PrecisionResult(
                precision=0.0,
                true_positives=0,
                false_positives=0,
                support=0,
                threshold=threshold,
                warning="NO_POSITIVE_PREDICTIONS",
                explanation="Precision represents the proportion of predicted fraud transactions that were actually fraudulent.",  # noqa: E501
            )

        prec_raw = tp / float(support)
        precision_score = round(max(0.0, min(1.0, prec_raw)), 6)

        return PrecisionResult(
            precision=precision_score,
            true_positives=tp,
            false_positives=fp,
            support=support,
            threshold=threshold,
            warning=None,
            explanation="Precision represents the proportion of predicted fraud transactions that were actually fraudulent.",  # noqa: E501
        )
