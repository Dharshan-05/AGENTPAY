"""F1 Score Evaluator Engine (Phase 239)."""

from __future__ import annotations

import logging

from app.schemas.ml_evaluation import F1Result

logger = logging.getLogger("fraudguard.ml.evaluation.f1")


class F1Evaluator:
    """Production F1 Score Evaluator with Frozen Threshold & Zero-Division Safety (Phase 239)."""

    def evaluate_f1(
        self,
        y_true: list[int],
        y_pred: list[int],
        threshold: float = 0.50,
        threshold_source: str = "CONFIGURATION",
    ) -> F1Result:
        """Calculate harmonic mean F1 score 2TP / (2TP + FP + FN) at frozen threshold (Phase 239)."""  # noqa: E501
        if len(y_true) != len(y_pred):
            raise ValueError(
                f"Ground truth length ({len(y_true)}) mismatches prediction length ({len(y_pred)})"
            )

        tp = 0
        fp = 0
        fn = 0

        for true_val, pred_val in zip(y_true, y_pred, strict=True):
            if pred_val == 1:
                if true_val == 1:
                    tp += 1
                else:
                    fp += 1
            else:
                if true_val == 1:
                    fn += 1

        denom = (2 * tp) + fp + fn

        if denom == 0:
            logger.warning(
                "F1 zero-division: No positive support (2TP + FP + FN = 0) at threshold %.2f",
                threshold,
            )
            return F1Result(
                f1=0.0,
                true_positives=0,
                false_positives=0,
                false_negatives=0,
                support=0,
                threshold=threshold,
                threshold_source=threshold_source,
                warning="NO_POSITIVE_SUPPORT",
                explanation="F1 score computed on the held-out test set using the frozen threshold.",  # noqa: E501
                metric_version="1.0.0",
            )

        f1_raw = (2 * tp) / float(denom)
        f1_score = round(max(0.0, min(1.0, f1_raw)), 6)

        return F1Result(
            f1=f1_score,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            support=denom,
            threshold=threshold,
            threshold_source=threshold_source,
            warning=None,
            explanation="F1 score computed on the held-out test set using the frozen threshold.",  # noqa: E501
            metric_version="1.0.0",
        )
