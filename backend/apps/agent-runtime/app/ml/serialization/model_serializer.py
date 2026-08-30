"""Production Model Serializer Engine with Cryptographic Verification (Phase 243)."""

from __future__ import annotations

import hashlib
import logging

import xgboost as xgb

from app.schemas.ml_evaluation import EvaluationManifest
from app.schemas.ml_serialization import SerializedArtifactManifest
from app.schemas.ml_training import ModelTrainingResult

logger = logging.getLogger("fraudguard.ml.serialization")


class ModelSerializer:
    """Production XGBoost Model Serializer with SHA-256 Checksum & Safe Loading (Phase 243)."""

    def serialize_model(
        self,
        model: xgb.XGBClassifier,
        training_result: ModelTrainingResult,
        evaluation_manifest: EvaluationManifest | None = None,
        model_id: str | None = None,
        model_version: str = "1.0.0",
    ) -> tuple[bytes, SerializedArtifactManifest]:
        """Serialize XGBoost model to bytes with cryptographic SHA-256 checksum (Phase 243)."""
        booster = getattr(model, "get_booster", lambda: model)()

        # Save model directly to raw JSON bytearray via save_raw()
        buf = booster.save_raw("json")
        artifact_bytes = bytes(buf)

        checksum = hashlib.sha256(artifact_bytes).hexdigest()
        size_bytes = len(artifact_bytes)
        m_id = model_id or f"model_{str(training_result.training_run_id)[:8]}"

        manifest = SerializedArtifactManifest(
            model_id=m_id,
            model_version=model_version,
            model_family="XGBoost",
            format="json",
            feature_names=training_result.feature_names,
            feature_versions=training_result.feature_versions,
            dataset_fingerprint=training_result.dataset_fingerprint,
            training_run_id=training_result.training_run_id,
            optimization_run_id=None,
            evaluation_id=evaluation_manifest.evaluation_id if evaluation_manifest else None,
            configuration_hash=training_result.dataset_fingerprint,
            serializer_version="1.0.0",
            checksum=checksum,
            artifact_size_bytes=size_bytes,
        )

        logger.info(
            "Serialized model %s (v%s, size=%d bytes, SHA-256=%s)",
            m_id,
            model_version,
            size_bytes,
            checksum[:12],
        )

        return artifact_bytes, manifest

    def verify_checksum(self, artifact_bytes: bytes, manifest: SerializedArtifactManifest) -> bool:
        """Verify artifact SHA-256 checksum integrity (Phase 243)."""
        if not artifact_bytes:
            return False
        computed = hashlib.sha256(artifact_bytes).hexdigest()
        return computed == manifest.checksum

    def deserialize_model(
        self,
        artifact_bytes: bytes,
        manifest: SerializedArtifactManifest,
        verify_contract: bool = True,
    ) -> xgb.XGBClassifier:
        """Safely deserialize XGBoost model artifact after verifying checksum and contract (Phase 243)."""  # noqa: E501
        if not artifact_bytes:
            raise ValueError("Artifact bytes buffer is empty.")

        # 1. Cryptographic SHA-256 Checksum Verification
        if not self.verify_checksum(artifact_bytes, manifest):
            computed = hashlib.sha256(artifact_bytes).hexdigest()
            logger.error(
                "Cryptographic checksum mismatch! Tampered artifact! (expected=%s, computed=%s)",
                manifest.checksum,
                computed,
            )
            raise ValueError("Checksum mismatch! Tampered or corrupted artifact detected.")

        # 2. Safe Deserialization via XGBClassifier
        model = xgb.XGBClassifier()
        buf = bytearray(artifact_bytes)
        model.load_model(buf)
        booster = model.get_booster()

        # 3. Verify Feature Contract
        if verify_contract:
            f_names = booster.feature_names
            if f_names and len(f_names) != len(manifest.feature_names):
                raise ValueError(
                    f"Deserialized model feature count ({len(f_names)}) mismatches manifest ({len(manifest.feature_names)})"  # noqa: E501
                )

        logger.info(
            "Successfully deserialized model %s (v%s, checksum=%s)",
            manifest.model_id,
            manifest.model_version,
            manifest.checksum[:12],
        )

        return model
