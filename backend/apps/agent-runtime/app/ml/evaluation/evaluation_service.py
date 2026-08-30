"""Production Model Evaluation Service (Phases 236-242)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from typing import Any

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.dataset.training_dataset_builder import TrainingDataset
from app.ml.evaluation.confusion_matrix_evaluator import ConfusionMatrixEvaluator
from app.ml.evaluation.f1_evaluator import F1Evaluator
from app.ml.evaluation.pr_auc_evaluator import PrAucEvaluator
from app.ml.evaluation.precision_evaluator import PrecisionEvaluator
from app.ml.evaluation.recall_evaluator import RecallEvaluator
from app.ml.evaluation.roc_auc_evaluator import RocAucEvaluator
from app.ml.training.xgboost_trainer import XGBoostTrainer
from app.schemas.ml_evaluation import (  # noqa: E501
    EvaluationManifest,
    EvaluationResult,
    EvaluationThresholdConfig,
)
from app.schemas.ml_training import ModelTrainingResult

logger = logging.getLogger("fraudguard.ml.evaluation")


class ModelEvaluationService:
    """Production Model Evaluation Service with Full Metric Framework (Phases 236-242)."""

    def __init__(
        self,
        config: MLPipelineConfig | None = None,
        precision_evaluator: PrecisionEvaluator | None = None,
        recall_evaluator: RecallEvaluator | None = None,
        f1_evaluator: F1Evaluator | None = None,
        roc_auc_evaluator: RocAucEvaluator | None = None,
        pr_auc_evaluator: PrAucEvaluator | None = None,
        confusion_matrix_evaluator: ConfusionMatrixEvaluator | None = None,
        trainer: XGBoostTrainer | None = None,
    ) -> None:
        self.config = config or get_default_ml_config()
        self.precision_evaluator = precision_evaluator or PrecisionEvaluator()
        self.recall_evaluator = recall_evaluator or RecallEvaluator()
        self.f1_evaluator = f1_evaluator or F1Evaluator()
        self.roc_auc_evaluator = roc_auc_evaluator or RocAucEvaluator()
        self.pr_auc_evaluator = pr_auc_evaluator or PrAucEvaluator()
        self.confusion_matrix_evaluator = confusion_matrix_evaluator or ConfusionMatrixEvaluator()
        self.trainer = trainer or XGBoostTrainer(config=self.config)

    def evaluate_model(
        self,
        model: Any,
        training_result: ModelTrainingResult,
        target_dataset: TrainingDataset,
        threshold_config: EvaluationThresholdConfig | None = None,
        partition_name: str = "TEST",
    ) -> tuple[EvaluationResult, EvaluationManifest]:
        """Evaluate candidate model on target dataset split with complete metric framework (Phases 236-242)."""  # noqa: E501
        logger.info(
            "Evaluating model run %s on partition %s (%d samples)",
            training_result.training_run_id,
            partition_name,
            len(target_dataset.X),
        )

        if not target_dataset.X or not target_dataset.y:
            raise ValueError("Evaluation target dataset cannot be empty.")

        # 1. Dataset & Model Contract Validation
        if training_result.dataset_fingerprint != target_dataset.manifest.dataset_fingerprint:
            raise ValueError(
                f"Dataset fingerprint mismatch! Model trained on '{training_result.dataset_fingerprint}', got target '{target_dataset.manifest.dataset_fingerprint}'"  # noqa: E501
            )

        # Feature Count & Name Order Integrity Check
        if training_result.feature_names != target_dataset.feature_names:
            raise ValueError(
                f"Feature order/name mismatch! Model expected features {training_result.feature_names}, got {target_dataset.feature_names}"  # noqa: E501
            )

        thresh_cfg = threshold_config or EvaluationThresholdConfig(
            threshold=0.50, threshold_source="CONFIGURATION"
        )
        cutoff = thresh_cfg.threshold

        # 2. Convert Data to Numeric Numpy Matrix via trainer helper (preserving order integrity)
        X_mat = self.trainer._convert_to_matrix(target_dataset.X, training_result.feature_names)
        y_true = list(target_dataset.y)

        # 3. Generate Probabilities & Assert Probability Bounds
        if not hasattr(model, "predict_proba"):
            raise ValueError("Candidate model does not support predict_proba() interface.")

        probs_raw = model.predict_proba(X_mat)[:, 1]
        y_probs: list[float] = []
        y_preds: list[int] = []

        for idx, p in enumerate(probs_raw):
            f_p = float(p)
            if math.isnan(f_p) or math.isinf(f_p) or f_p < 0.0 or f_p > 1.0:
                raise ValueError(
                    f"Probability boundary error: sample {idx} emitted invalid probability {f_p}"
                )
            y_probs.append(f_p)
            y_preds.append(1 if f_p >= cutoff else 0)

        # 4. Phase 237-242 Metric Evaluations
        precision_res = self.precision_evaluator.evaluate_precision(
            y_true, y_preds, threshold=cutoff
        )
        recall_res = self.recall_evaluator.evaluate_recall(y_true, y_preds, threshold=cutoff)
        f1_res = self.f1_evaluator.evaluate_f1(
            y_true, y_preds, threshold=cutoff, threshold_source=thresh_cfg.threshold_source
        )
        roc_auc_res = self.roc_auc_evaluator.evaluate_roc_auc(y_true, y_probs)
        pr_auc_res = self.pr_auc_evaluator.evaluate_pr_auc(y_true, y_probs)
        cm_res = self.confusion_matrix_evaluator.evaluate_confusion_matrix(
            y_true, y_preds, threshold=cutoff, threshold_source=thresh_cfg.threshold_source
        )

        pos_samples = y_true.count(1)
        neg_samples = y_true.count(0)
        pred_pos = y_preds.count(1)
        pred_neg = y_preds.count(0)

        eval_id = uuid.uuid4()
        result = EvaluationResult(
            evaluation_id=eval_id,
            model_candidate_id=str(training_result.training_run_id),
            model_type=training_result.model_type,
            dataset_fingerprint=training_result.dataset_fingerprint,
            split_partition=partition_name,
            feature_count=len(training_result.feature_names),
            feature_names=training_result.feature_names,
            sample_count=len(y_true),
            positive_samples=pos_samples,
            negative_samples=neg_samples,
            predicted_positives=pred_pos,
            predicted_negatives=pred_neg,
            threshold_config=thresh_cfg,
            precision_result=precision_res,
            recall_result=recall_res,
            f1_result=f1_res,
            roc_auc_result=roc_auc_res,
            pr_auc_result=pr_auc_res,
            confusion_matrix_result=cm_res,
            status="SUCCEEDED",
        )

        config_payload = {
            "model_run_id": str(training_result.training_run_id),
            "fingerprint": training_result.dataset_fingerprint,
            "threshold": cutoff,
            "threshold_source": thresh_cfg.threshold_source,
            "features": training_result.feature_names,
        }
        cfg_hash = hashlib.sha256(json.dumps(config_payload, sort_keys=True).encode()).hexdigest()

        manifest = EvaluationManifest(
            evaluation_id=eval_id,
            model_candidate_id=str(training_result.training_run_id),
            dataset_fingerprint=training_result.dataset_fingerprint,
            split_id=target_dataset.manifest.training_dataset_id,
            feature_versions=training_result.feature_versions,
            feature_names=training_result.feature_names,
            threshold=cutoff,
            threshold_source=thresh_cfg.threshold_source,
            sample_count=len(y_true),
            positive_count=pos_samples,
            negative_count=neg_samples,
            precision=precision_res.precision,
            recall=recall_res.recall,
            f1=f1_res.f1,
            roc_auc=roc_auc_res.roc_auc,
            pr_auc=pr_auc_res.pr_auc,
            tp=cm_res.true_positives,
            tn=cm_res.true_negatives,
            fp=cm_res.false_positives,
            fn=cm_res.false_negatives,
            configuration_hash=cfg_hash,
        )

        logger.info(
            "Evaluation complete (Run ID: %s, partition: %s, precision: %.4f, recall: %.4f, F1: %.4f)",  # noqa: E501
            eval_id,
            partition_name,
            precision_res.precision,
            recall_res.recall,
            f1_res.f1,
        )

        return result, manifest
