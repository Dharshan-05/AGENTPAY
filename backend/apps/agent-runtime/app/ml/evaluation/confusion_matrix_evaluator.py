"""Confusion Matrix Evaluator Engine (Phase 242)."""

from __future__ import annotations

import logging

from app.schemas.ml_evaluation import ConfusionMatrixResult

logger = logging.getLogger("fraudguard.ml.evaluation.confusion_matrix")


class ConfusionMatrixEvaluator:
    """Production Confusion Matrix Evaluator with Frozen Threshold & Zero-Denominator Safety (Phase 242)."""  # noqa: E501

    def evaluate_confusion_matrix(
        self,
        y_true: list[int],
        y_pred: list[int],
        threshold: float = 0.50,
        threshold_source: str = "CONFIGURATION",
    ) -> ConfusionMatrixResult:
        """Calculate TP, TN, FP, FN and normalized rates at frozen threshold (Phase 242)."""
        if len(y_true) != len(y_pred):
            raise ValueError(
                f"Ground truth length ({len(y_true)}) mismatches prediction length ({len(y_pred)})"
            )

        sample_count = len(y_true)
        if sample_count == 0:
            return ConfusionMatrixResult(
                true_positives=0,
                true_negatives=0,
                false_positives=0,
                false_negatives=0,
                total_samples=0,
                positive_support=0,
                negative_support=0,
                predicted_positives=0,
                predicted_negatives=0,
                true_positive_rate=None,
                true_negative_rate=None,
                false_positive_rate=None,
                false_negative_rate=None,
                threshold=threshold,
                threshold_source=threshold_source,
                warning="EMPTY_DATASET",
                explanation="Confusion matrix cannot be evaluated on an empty dataset.",
                metric_version="1.0.0",
            )

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for true_val, pred_val in zip(y_true, y_pred, strict=True):
            if true_val == 1 and pred_val == 1:
                tp += 1
            elif true_val == 0 and pred_val == 0:
                tn += 1
            elif true_val == 0 and pred_val == 1:
                fp += 1
            elif true_val == 1 and pred_val == 0:
                fn += 1

        pos_support = tp + fn
        neg_support = tn + fp
        pred_pos = tp + fp
        pred_neg = tn + fn

        tpr = round(tp / float(pos_support), 6) if pos_support > 0 else None
        tnr = round(tn / float(neg_support), 6) if neg_support > 0 else None
        fpr = round(fp / float(neg_support), 6) if neg_support > 0 else None
        fnr = round(fn / float(pos_support), 6) if pos_support > 0 else None

        warning = None
        if pos_support == 0:
            warning = "ZERO_POSITIVE_SUPPORT"
        elif neg_support == 0:
            warning = "ZERO_NEGATIVE_SUPPORT"
        elif pred_pos == 0:
            warning = "NO_POSITIVE_PREDICTIONS"
        elif pred_neg == 0:
            warning = "NO_NEGATIVE_PREDICTIONS"

        return ConfusionMatrixResult(
            true_positives=tp,
            true_negatives=tn,
            false_positives=fp,
            false_negatives=fn,
            total_samples=sample_count,
            positive_support=pos_support,
            negative_support=neg_support,
            predicted_positives=pred_pos,
            predicted_negatives=pred_neg,
            true_positive_rate=tpr,
            true_negative_rate=tnr,
            false_positive_rate=fpr,
            false_negative_rate=fnr,
            threshold=threshold,
            threshold_source=threshold_source,
            warning=warning,
            explanation=f"Confusion matrix evaluated at frozen threshold {threshold:.2f} (TP={tp}, TN={tn}, FP={fp}, FN={fn}).",  # noqa: E501
            metric_version="1.0.0",
        )
