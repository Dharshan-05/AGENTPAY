"""Production SHAP Explainer Integration Service (Phase 256)."""

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
from app.schemas.ml_xai import PROHIBITED_LEAKAGE_FEATURES, ShapAttributionResult, ShapConfig

logger = logging.getLogger("fraudguard.ml.xai.shap")


class ShapIntegrationService:
    """Production SHAP Integration Service with Model Verification & Contract Safety (Phase 256)."""  # noqa: E501

    def __init__(
        self,
        registry: ModelRegistry,
        serializer: ModelSerializer | None = None,
        config: ShapConfig | None = None,
    ) -> None:
        self.registry = registry
        self.serializer = serializer or ModelSerializer()
        self.config = config or ShapConfig()

    def calculate_shap_attributions(
        self,
        tenant_id: uuid.UUID,
        model_name: str,
        X_matrix: np.ndarray[Any, Any],
        feature_names: list[str],
        prediction_probability: float,
        agent_id: uuid.UUID | None = None,
        transaction_id: str | None = None,
        target_model_version: str | None = None,
    ) -> ShapAttributionResult:
        """Calculate exact SHAP values for validated model & feature matrix (Phase 256)."""
        logger.info(
            "Calculating SHAP attributions for model %s (tenant=%s, tx=%s)",
            model_name,
            tenant_id,
            transaction_id,
        )

        # 1. Prohibited Feature Rejection (Data Leakage Guard)
        forbidden_present = set(feature_names).intersection(PROHIBITED_LEAKAGE_FEATURES)
        if forbidden_present:
            logger.error(
                "Data leakage error: prohibited features present in SHAP input: %s",
                forbidden_present,
            )  # noqa: E501
            raise ValueError(
                f"Prohibited data leakage feature present in input: {sorted(list(forbidden_present))}"  # noqa: E501
            )  # noqa: E501

        # 2. Model Resolution & Verification
        if target_model_version:
            reg_manifest = self.registry.get_model(tenant_id, model_name, target_model_version)
        else:
            reg_manifest = self.registry.resolve_production_model(tenant_id, model_name)

        if reg_manifest.lifecycle_state not in ("PRODUCTION", "STAGING", "REGISTERED"):
            raise ValueError(
                f"Model state '{reg_manifest.lifecycle_state}' is ineligible for SHAP explanation."
            )  # noqa: E501

        # 3. Cryptographic Artifact Checksum Verification
        if not self.registry.verify_model_artifact(
            tenant_id, model_name, reg_manifest.model_version
        ):  # noqa: E501
            raise ValueError(
                "Model artifact checksum verification failed! Tampered artifact rejected."
            )  # noqa: E501

        # 4. Deserialize Model Artifact
        art_bytes = self.registry._get_tenant_artifacts(tenant_id)[
            (model_name, reg_manifest.model_version)
        ]  # noqa: E501
        model = self.serializer.deserialize_model(art_bytes, reg_manifest.artifact_manifest)

        # 5. Exact Feature Contract & Order Verification
        expected_features = reg_manifest.artifact_manifest.feature_names
        if feature_names != expected_features:
            logger.error(
                "Feature contract mismatch! Expected %s, got %s", expected_features, feature_names
            )  # noqa: E501
            raise ValueError(
                f"Feature contract mismatch! Model expects features {expected_features}, got {feature_names}"  # noqa: E501
            )  # noqa: E501

        if X_matrix.shape[1] != len(expected_features):
            raise ValueError(
                f"Feature matrix dimension mismatch: shape {X_matrix.shape} != expected cols {len(expected_features)}"  # noqa: E501
            )  # noqa: E501

        # Check matrix for NaN or Inf
        if np.isnan(X_matrix).any() or np.isinf(X_matrix).any():
            raise ValueError("Feature matrix contains NaN or Infinity values.")

        # 6. Initialize SHAP TreeExplainer & Calculate SHAP values
        booster = getattr(model, "get_booster", lambda: model)()
        explainer = shap.TreeExplainer(booster)
        raw_shap = explainer.shap_values(X_matrix)

        # Process SHAP outputs
        shap_arr = np.array(raw_shap)
        if shap_arr.ndim == 2 and shap_arr.shape[0] == 1:
            shap_vector = shap_arr[0]
        elif shap_arr.ndim == 3 and shap_arr.shape[0] == 1:
            shap_vector = shap_arr[0, :, 1]  # positive class
        else:
            shap_vector = shap_arr.flatten()

        if len(shap_vector) != len(expected_features):
            raise ValueError(
                f"SHAP output length ({len(shap_vector)}) mismatches feature count ({len(expected_features)})"  # noqa: E501
            )  # noqa: E501

        shap_values_list: list[float] = []
        for idx, val in enumerate(shap_vector):
            f_val = float(val)
            if math.isnan(f_val) or math.isinf(f_val):
                raise ValueError(f"SHAP value calculation emitted NaN/Inf at index {idx}")
            shap_values_list.append(round(f_val, 6))

        base_val = float(explainer.expected_value)
        if isinstance(explainer.expected_value, (np.ndarray, list)):
            base_val = float(explainer.expected_value[0])

        exp_id = uuid.uuid4()
        now = datetime.now(UTC)

        cfg_payload = {
            "explainer_type": self.config.explainer_type,
            "output_space": self.config.output_space,
            "version": self.config.configuration_version,
        }
        cfg_hash = hashlib.sha256(json.dumps(cfg_payload, sort_keys=True).encode()).hexdigest()

        res_payload = {
            "model_version": reg_manifest.model_version,
            "artifact_checksum": reg_manifest.artifact_manifest.checksum,
            "shap_values": shap_values_list,
            "tenant_id": str(tenant_id),
            "transaction_id": transaction_id,
        }
        res_hash = hashlib.sha256(json.dumps(res_payload, sort_keys=True).encode()).hexdigest()

        return ShapAttributionResult(
            explanation_id=exp_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            model_name=model_name,
            model_version=reg_manifest.model_version,
            artifact_checksum=reg_manifest.artifact_manifest.checksum,
            feature_names=expected_features,
            feature_versions=reg_manifest.artifact_manifest.feature_versions,
            shap_values=shap_values_list,
            base_value=round(base_val, 6),
            prediction_probability=round(prediction_probability, 6),
            output_space=self.config.output_space,
            configuration_hash=cfg_hash,
            result_fingerprint=res_hash,
            created_at=now,
        )
