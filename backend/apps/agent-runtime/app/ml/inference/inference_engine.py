"""Production FraudGuard ML Inference Engine (Phase 246)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from datetime import UTC, datetime

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.inference.transformation import InferenceFeatureTransformer
from app.ml.registry.model_registry import ModelRegistry
from app.ml.serialization.model_serializer import ModelSerializer
from app.schemas.ml_inference import InferenceManifest, InferenceRequest, InferenceResult
from app.schemas.ml_versioning import ModelLifecycleState

logger = logging.getLogger("fraudguard.ml.inference.engine")


class FraudGuardInferenceEngine:
    """Production FraudGuard Inference Engine with Model Resolution & Audit Trail (Phase 246)."""

    def __init__(
        self,
        registry: ModelRegistry,
        serializer: ModelSerializer | None = None,
        transformer: InferenceFeatureTransformer | None = None,
        config: MLPipelineConfig | None = None,
    ) -> None:
        self.registry = registry
        self.serializer = serializer or ModelSerializer()
        self.transformer = transformer or InferenceFeatureTransformer()
        self.config = config or get_default_ml_config()

    def _compute_request_fingerprint(self, request: InferenceRequest) -> str:
        """Compute canonical SHA-256 fingerprint hash of inference request payload."""
        payload = {
            "tenant_id": str(request.tenant_id),
            "agent_id": str(request.agent_id) if request.agent_id else None,
            "transaction_id": request.transaction_id,
            "model_name": request.model_name,
            "feature_values": {k: str(v) for k, v in sorted(request.feature_values.items())},
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def predict_fraud(self, request: InferenceRequest) -> tuple[InferenceResult, InferenceManifest]:
        """Execute real-time FraudGuard ML prediction for production request (Phase 246)."""
        logger.info(
            "Executing FraudGuard inference for tx %s (tenant=%s)",
            request.transaction_id,
            request.tenant_id,
        )

        req_fingerprint = self._compute_request_fingerprint(request)

        # 1. Resolve Active PRODUCTION Model for Tenant
        reg_manifest = self.registry.resolve_production_model(
            tenant_id=request.tenant_id, model_name=request.model_name
        )

        # 2. Lifecycle State Enforcement (Must be PRODUCTION)
        if reg_manifest.lifecycle_state != ModelLifecycleState.PRODUCTION:
            logger.error(
                "Non-production model resolution attempt for tenant %s (state=%s)",
                request.tenant_id,
                reg_manifest.lifecycle_state,
            )
            raise ValueError(
                f"Model '{request.model_name}' is in state '{reg_manifest.lifecycle_state}'. Only PRODUCTION models may serve inference!"  # noqa: E501
            )

        # 3. Cryptographic Artifact Checksum Verification
        if not self.registry.verify_model_artifact(
            request.tenant_id, request.model_name, reg_manifest.model_version
        ):
            raise ValueError(
                "Model artifact checksum verification failed! Tampered model rejected."
            )  # noqa: E501

        # 4. Deserialize Model Artifact
        art_bytes = self.registry._get_tenant_artifacts(request.tenant_id)[
            (request.model_name, reg_manifest.model_version)
        ]
        model = self.serializer.deserialize_model(art_bytes, reg_manifest.artifact_manifest)

        # 5. Transform Inference Request into Validated Numeric Feature Matrix
        expected_features = reg_manifest.artifact_manifest.feature_names
        expected_versions = reg_manifest.artifact_manifest.feature_versions

        X_matrix = self.transformer.transform_request(
            request=request,
            expected_feature_names=expected_features,
            expected_feature_versions=expected_versions,
        )

        # 6. Model Prediction & Probability Boundary Validation
        probs_raw = model.predict_proba(X_matrix)[0, 1]
        fraud_prob = float(probs_raw)

        if math.isnan(fraud_prob) or math.isinf(fraud_prob) or fraud_prob < 0.0 or fraud_prob > 1.0:
            raise ValueError(
                f"Probability boundary error: model emitted invalid probability {fraud_prob}"
            )  # noqa: E501

        fraud_prob = round(fraud_prob, 6)
        inf_id = uuid.uuid4()
        inf_time = datetime.now(UTC)

        # 7. Construct Inference Result & Immutable Audit Manifest
        result = InferenceResult(
            inference_id=inf_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            model_id=reg_manifest.artifact_manifest.model_id,
            model_version=reg_manifest.model_version,
            feature_versions=expected_versions,
            prediction_timestamp=request.prediction_timestamp,
            fraud_probability=fraud_prob,
            inference_timestamp=inf_time,
            configuration_hash=reg_manifest.evaluation_manifest.configuration_hash,
            request_fingerprint=req_fingerprint,
            status="SUCCEEDED",
        )

        res_payload = {
            "fraud_probability": fraud_prob,
            "model_version": reg_manifest.model_version,
            "request_fingerprint": req_fingerprint,
            "tenant_id": str(request.tenant_id),
        }
        res_fingerprint = hashlib.sha256(
            json.dumps(res_payload, sort_keys=True).encode()
        ).hexdigest()  # noqa: E501

        manifest = InferenceManifest(
            inference_id=inf_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            model_version=reg_manifest.model_version,
            artifact_checksum=reg_manifest.artifact_manifest.checksum,
            feature_versions=expected_versions,
            preprocessing_version="2.0",
            transformation_version="1.0.0",
            prediction_timestamp=request.prediction_timestamp,
            inference_timestamp=inf_time,
            fraud_probability=fraud_prob,
            configuration_hash=reg_manifest.evaluation_manifest.configuration_hash,
            request_fingerprint=req_fingerprint,
            result_fingerprint=res_fingerprint,
        )

        logger.info(
            "Inference complete for tx %s (model=v%s, P(fraud)=%.4f)",
            request.transaction_id,
            reg_manifest.model_version,
            fraud_prob,
        )

        return result, manifest
