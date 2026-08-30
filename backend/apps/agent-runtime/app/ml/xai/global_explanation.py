"""Global Model Explanation Service (Phase 259)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import UTC, datetime
from typing import Any

import numpy as np
import shap

from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.schemas.ml_xai import (
    PROHIBITED_LEAKAGE_FEATURES,
    GlobalFeatureImportance,
    GlobalModelExplanation,
    ShapConfig,
)

logger = logging.getLogger("fraudguard.ml.xai.global")


class GlobalModelExplanationService:
    """Production Global Model Explanation Service (Phase 259)."""

    def __init__(
        self,
        registry: ModelRegistry,
        serializer: ModelSerializer | None = None,
        config: ShapConfig | None = None,
    ) -> None:
        self.registry = registry
        self.serializer = serializer or ModelSerializer()
        self.config = config or ShapConfig()

    def generate_global_explanation(
        self,
        tenant_id: uuid.UUID,
        model_name: str,
        target_model_version: str,
        X_matrix: np.ndarray[Any, Any],
        feature_names: list[str],
        dataset_fingerprint: str,
        feature_versions: dict[str, str] | None = None,
    ) -> GlobalModelExplanation:
        """Generate aggregate global feature importance explanation across dataset (Phase 259)."""
        logger.info(
            "Generating global model explanation for %s v%s (samples=%d, tenant=%s)",
            model_name,
            target_model_version,
            X_matrix.shape[0],
            tenant_id,
        )

        # 1. Prohibited Feature / Target Leakage Validation
        forbidden_present = set(feature_names).intersection(PROHIBITED_LEAKAGE_FEATURES)
        if forbidden_present:
            raise ValueError(
                f"Prohibited data leakage feature present in global dataset: {sorted(list(forbidden_present))}"  # noqa: E501
            )  # noqa: E501

        # 2. Model Resolution & Artifact Checksum Verification
        reg_manifest = self.registry.get_model(tenant_id, model_name, target_model_version)
        if reg_manifest.lifecycle_state not in ("PRODUCTION", "STAGING", "REGISTERED"):
            raise ValueError(
                f"Model state '{reg_manifest.lifecycle_state}' is ineligible for global explanation."  # noqa: E501
            )  # noqa: E501

        if not self.registry.verify_model_artifact(tenant_id, model_name, target_model_version):
            raise ValueError("Model artifact checksum verification failed!")

        # 3. Deserialize Model Artifact
        art_bytes = self.registry._get_tenant_artifacts(tenant_id)[
            (model_name, target_model_version)
        ]  # noqa: E501
        model = self.serializer.deserialize_model(art_bytes, reg_manifest.artifact_manifest)

        # 4. Feature Contract Verification
        expected_features = reg_manifest.artifact_manifest.feature_names
        if feature_names != expected_features:
            raise ValueError(
                f"Feature contract mismatch! Model expects {expected_features}, got {feature_names}"
            )  # noqa: E501

        if X_matrix.shape[1] != len(expected_features):
            raise ValueError(
                f"Feature matrix dimension mismatch: shape {X_matrix.shape} != cols {len(expected_features)}"  # noqa: E501
            )  # noqa: E501

        if np.isnan(X_matrix).any() or np.isinf(X_matrix).any():
            raise ValueError("Global explanation dataset contains NaN or Infinity values.")

        # 5. TreeExplainer Aggregate SHAP Calculation
        booster = getattr(model, "get_booster", lambda: model)()
        explainer = shap.TreeExplainer(booster)
        raw_shap = explainer.shap_values(X_matrix)

        shap_arr = np.array(raw_shap)
        if shap_arr.ndim == 3:
            shap_arr = shap_arr[:, :, 1]  # positive class for binary classification

        # Calculate mean(abs(SHAP)) per feature
        mean_abs_shap = np.mean(np.abs(shap_arr), axis=0)
        total_mean_abs = float(np.sum(mean_abs_shap))

        items: list[dict[str, Any]] = []
        f_vers = feature_versions or reg_manifest.artifact_manifest.feature_versions

        for f_name, mean_val in zip(expected_features, mean_abs_shap, strict=True):
            m_val = round(float(mean_val), 6)
            if math.isnan(m_val) or math.isinf(m_val):
                raise ValueError(
                    f"Mean absolute SHAP calculation emitted NaN/Inf for feature '{f_name}'"
                )  # noqa: E501

            rel_imp = (
                min(1.0, max(0.0, round(m_val / total_mean_abs, 6))) if total_mean_abs > 0 else 0.0
            )  # noqa: E501
            ver = f_vers.get(f_name, "1.0.0")

            items.append(
                {
                    "feature_name": f_name,
                    "feature_version": ver,
                    "mean_absolute_shap": m_val,
                    "relative_importance": rel_imp,
                }
            )

        # 6. Deterministic Sorting: 1. mean_absolute_shap descending, 2. feature_name ascending
        items.sort(key=lambda x: (-x["mean_absolute_shap"], x["feature_name"]))

        global_importances: list[GlobalFeatureImportance] = []
        for rank_idx, item in enumerate(items, start=1):
            global_importances.append(
                GlobalFeatureImportance(
                    feature_name=item["feature_name"],
                    feature_version=item["feature_version"],
                    mean_absolute_shap=item["mean_absolute_shap"],
                    relative_importance=item["relative_importance"],
                    rank=rank_idx,
                )
            )

        top_feature = global_importances[0].feature_name if global_importances else "N/A"
        stmt = (
            f"Feature '{top_feature}' has the highest average contribution to the model's output "
            f"within the analyzed explanation dataset ({X_matrix.shape[0]} samples, model v{target_model_version})."  # noqa: E501
        )

        exp_id = uuid.uuid4()
        now = datetime.now(UTC)

        cfg_payload = {
            "explainer_type": self.config.explainer_type,
            "version": self.config.configuration_version,
            "sample_count": X_matrix.shape[0],
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "model_version": target_model_version,
            "artifact_checksum": reg_manifest.artifact_manifest.checksum,
            "dataset_fingerprint": dataset_fingerprint,
            "top_feature": top_feature,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return GlobalModelExplanation(
            explanation_id=exp_id,
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=target_model_version,
            artifact_checksum=reg_manifest.artifact_manifest.checksum,
            dataset_fingerprint=dataset_fingerprint,
            feature_versions=f_vers,
            sample_count=X_matrix.shape[0],
            feature_count=len(expected_features),
            feature_importance=global_importances,
            explanation_statement=stmt,
            configuration_hash=cfg_hash,
            result_fingerprint=res_hash,
            created_at=now,
        )
