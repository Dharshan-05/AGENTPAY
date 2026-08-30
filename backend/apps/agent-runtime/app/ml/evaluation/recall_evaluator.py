"""Recall Evaluator Engine (Phase 238)."""

from __future__ import annotations

import logging

from app.schemas.ml_evaluation import RecallResult

logger = logging.getLogger("fraudguard.ml.evaluation.recall")


class RecallEvaluator:
    """Production Recall Evaluator with Zero-Division Safety & Bounds Verification (Phase 238)."""

    def evaluate_recall(
        self,
        y_true: list[int],
        y_pred: list[int],
        threshold: float = 0.50,
    ) -> RecallResult:
        """Calculate recall score TP / (TP + FN) with zero-division protection (Phase 238)."""
        if len(y_true) != len(y_pred):
            raise ValueError(
                f"Ground truth length ({len(y_true)}) mismatches prediction length ({len(y_pred)})"
            )

        tp = 0
        fn = 0

        for true_val, pred_val in zip(y_true, y_pred, strict=True):
            if true_val == 1:
                if pred_val == 1:
                    tp += 1
                else:
                    fn += 1

        support = tp + fn

        if support == 0:
            logger.warning("Recall zero-division: No positive ground truth fraud instances found.")
            return RecallResult(
                recall=0.0,
                true_positives=0,
                false_negatives=0,
                support=0,
                threshold=threshold,
                warning="NO_POSITIVE_GROUND_TRUTH",
                explanation="Recall represents the proportion of actual fraudulent transactions detected by the model.",  # noqa: E501
            )

        rec_raw = tp / float(support)
        recall_score = round(max(0.0, min(1.0, rec_raw)), 6)

        return RecallResult(
            recall=recall_score,
            true_positives=tp,
            false_negatives=fn,
            support=support,
            threshold=threshold,
            warning=None,
            explanation="Recall represents the proportion of actual fraudulent transactions detected by the model.",  # noqa: E501
        )
