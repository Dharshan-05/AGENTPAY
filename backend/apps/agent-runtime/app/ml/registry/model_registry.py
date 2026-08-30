"""Enterprise Model Registry Platform with Quality Gates & Tenant Isolation (Phase 245)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.ml.serialization.model_serializer import ModelSerializer
from app.ml.versioning.model_version_manager import ModelVersionManager
from app.schemas.ml_evaluation import EvaluationManifest
from app.schemas.ml_registry import QualityGateConfig, RegisteredModelManifest, RegistryAuditRecord
from app.schemas.ml_serialization import SerializedArtifactManifest
from app.schemas.ml_versioning import ModelLifecycleState, ModelVersionRecord

logger = logging.getLogger("fraudguard.ml.registry")


class ModelRegistry:
    """Production ML Model Registry with Quality Gates, Lineage, & Tenant Isolation (Phase 245)."""

    def __init__(self, serializer: ModelSerializer | None = None) -> None:
        self.serializer = serializer or ModelSerializer()
        self.version_manager = ModelVersionManager()
        # Storage maps keyed by tenant_id
        # _records[tenant_id][(model_name, model_version)] = RegisteredModelManifest
        self._records: dict[uuid.UUID, dict[tuple[str, str], RegisteredModelManifest]] = {}
        # _artifacts[tenant_id][(model_name, model_version)] = bytes
        self._artifacts: dict[uuid.UUID, dict[tuple[str, str], bytes]] = {}
        # _audit_logs[tenant_id] = list[RegistryAuditRecord]
        self._audit_logs: dict[uuid.UUID, list[RegistryAuditRecord]] = {}

    def _get_tenant_records(
        self, tenant_id: uuid.UUID
    ) -> dict[tuple[str, str], RegisteredModelManifest]:
        """Get or initialize tenant-scoped records map."""
        if tenant_id not in self._records:
            self._records[tenant_id] = {}
        return self._records[tenant_id]

    def _get_tenant_artifacts(self, tenant_id: uuid.UUID) -> dict[tuple[str, str], bytes]:
        """Get or initialize tenant-scoped artifacts map."""
        if tenant_id not in self._artifacts:
            self._artifacts[tenant_id] = {}
        return self._artifacts[tenant_id]

    def _get_tenant_audit(self, tenant_id: uuid.UUID) -> list[RegistryAuditRecord]:
        """Get or initialize tenant-scoped audit trail."""
        if tenant_id not in self._audit_logs:
            self._audit_logs[tenant_id] = []
        return self._audit_logs[tenant_id]

    def _log_audit(
        self,
        tenant_id: uuid.UUID,
        model_name: str,
        model_version: str,
        action: str,
        previous_state: str,
        new_state: str,
    ) -> None:
        """Append immutable audit log entry for tenant model lifecycle event."""
        rec = RegistryAuditRecord(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
        )
        self._get_tenant_audit(tenant_id).append(rec)

    def register_model(
        self,
        tenant_id: uuid.UUID,
        model_name: str,
        model_version: str,
        raw_bytes: bytes,
        artifact_manifest: SerializedArtifactManifest,
        evaluation_manifest: EvaluationManifest,
    ) -> RegisteredModelManifest:
        """Register model version with artifact checksum and contract validation (Phase 245)."""  # noqa: E501
        if not raw_bytes:
            raise ValueError("Registration artifact bytes cannot be empty.")

        # 1. Cryptographic Checksum Integrity Verification
        if not self.serializer.verify_checksum(raw_bytes, artifact_manifest):
            raise ValueError("Checksum verification failed! Tampered artifact rejected.")

        # 2. Dataset & Feature Contract Completeness Check
        if not evaluation_manifest.dataset_fingerprint or not evaluation_manifest.feature_versions:
            raise ValueError(
                "Registration incomplete: evaluation manifest missing dataset fingerprint or feature versions!"  # noqa: E501
            )

        records = self._get_tenant_records(tenant_id)
        artifacts = self._get_tenant_artifacts(tenant_id)

        key = (model_name, model_version)
        if key in records:
            raise ValueError(
                f"Model version '{model_name}:v{model_version}' already exists for tenant {tenant_id}. Silent overwrite forbidden!"  # noqa: E501
            )

        manifest = RegisteredModelManifest(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            lifecycle_state=ModelLifecycleState.REGISTERED,
            artifact_manifest=artifact_manifest,
            evaluation_manifest=evaluation_manifest,
        )

        records[key] = manifest
        artifacts[key] = raw_bytes

        self._log_audit(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            action="REGISTER",
            previous_state="NONE",
            new_state=ModelLifecycleState.REGISTERED,
        )

        logger.info(
            "Registered model %s:v%s for tenant %s (SHA-256=%s)",
            model_name,
            model_version,
            tenant_id,
            artifact_manifest.checksum[:12],
        )

        return manifest

    def get_model(
        self, tenant_id: uuid.UUID, model_name: str, model_version: str
    ) -> RegisteredModelManifest:
        """Get model registration manifest with strict tenant isolation (Phase 245)."""
        records = self._get_tenant_records(tenant_id)
        key = (model_name, model_version)
        if key not in records:
            raise ValueError(f"Model '{model_name}:v{model_version}' not found for tenant.")
        return records[key]

    def promote_to_staging(
        self, tenant_id: uuid.UUID, model_name: str, model_version: str
    ) -> RegisteredModelManifest:
        """Promote model version to STAGING lifecycle state (Phase 245)."""
        manifest = self.get_model(tenant_id, model_name, model_version)
        current_state = manifest.lifecycle_state

        ver_rec = ModelVersionRecord(
            model_id=manifest.artifact_manifest.model_id,
            model_version=manifest.model_version,
            model_name=manifest.model_name,
            tenant_id=tenant_id,
            lifecycle_state=current_state,
            artifact_checksum=manifest.artifact_manifest.checksum,
            dataset_fingerprint=manifest.evaluation_manifest.dataset_fingerprint,
            feature_versions=manifest.evaluation_manifest.feature_versions,
            training_run_id=manifest.artifact_manifest.training_run_id,
            configuration_hash=manifest.evaluation_manifest.configuration_hash,
        )

        # Enforce valid lifecycle state transition
        updated_rec = self.version_manager.transition_state(ver_rec, ModelLifecycleState.STAGING)

        updated_manifest = manifest.model_copy(
            update={
                "lifecycle_state": updated_rec.lifecycle_state,
                "updated_at": datetime.now(UTC),
            }
        )

        self._records[tenant_id][(model_name, model_version)] = updated_manifest
        self._log_audit(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            action="PROMOTE_STAGING",
            previous_state=current_state,
            new_state=ModelLifecycleState.STAGING,
        )

        return updated_manifest

    def promote_to_production(
        self,
        tenant_id: uuid.UUID,
        model_name: str,
        model_version: str,
        quality_gates: QualityGateConfig | None = None,
    ) -> RegisteredModelManifest:
        """Promote model version to PRODUCTION state with Quality Gate Validation & Atomic Uniqueness (Phase 245)."""  # noqa: E501
        manifest = self.get_model(tenant_id, model_name, model_version)
        eval_m = manifest.evaluation_manifest

        # 1. Quality Gate Evaluation
        gates = quality_gates or QualityGateConfig()
        if eval_m.precision < gates.minimum_precision:
            raise ValueError(
                f"Quality Gate Failed: precision {eval_m.precision:.4f} < minimum {gates.minimum_precision:.4f}"  # noqa: E501
            )
        if eval_m.recall < gates.minimum_recall:
            raise ValueError(
                f"Quality Gate Failed: recall {eval_m.recall:.4f} < minimum {gates.minimum_recall:.4f}"  # noqa: E501
            )
        if eval_m.f1 is not None and eval_m.f1 < gates.minimum_f1:
            raise ValueError(
                f"Quality Gate Failed: F1 {eval_m.f1:.4f} < minimum {gates.minimum_f1:.4f}"
            )
        if eval_m.roc_auc is not None and eval_m.roc_auc < gates.minimum_roc_auc:
            raise ValueError(
                f"Quality Gate Failed: ROC-AUC {eval_m.roc_auc:.4f} < minimum {gates.minimum_roc_auc:.4f}"  # noqa: E501
            )
        if eval_m.pr_auc is not None and eval_m.pr_auc < gates.minimum_pr_auc:
            raise ValueError(
                f"Quality Gate Failed: PR-AUC {eval_m.pr_auc:.4f} < minimum {gates.minimum_pr_auc:.4f}"  # noqa: E501
            )

        current_state = manifest.lifecycle_state
        ver_rec = ModelVersionRecord(
            model_id=manifest.artifact_manifest.model_id,
            model_version=manifest.model_version,
            model_name=manifest.model_name,
            tenant_id=tenant_id,
            lifecycle_state=current_state,
            artifact_checksum=manifest.artifact_manifest.checksum,
            dataset_fingerprint=manifest.evaluation_manifest.dataset_fingerprint,
            feature_versions=manifest.evaluation_manifest.feature_versions,
            training_run_id=manifest.artifact_manifest.training_run_id,
            configuration_hash=manifest.evaluation_manifest.configuration_hash,
        )

        updated_rec = self.version_manager.transition_state(ver_rec, ModelLifecycleState.PRODUCTION)

        # 2. Atomic Production Model Uniqueness: Demote existing PRODUCTION model for model_name
        records = self._get_tenant_records(tenant_id)
        for (m_name, m_ver), item in list(records.items()):
            if m_name == model_name and item.lifecycle_state == ModelLifecycleState.PRODUCTION:
                if m_ver != model_version:
                    demoted_item = item.model_copy(
                        update={
                            "lifecycle_state": ModelLifecycleState.DEPRECATED,
                            "updated_at": datetime.now(UTC),
                        }
                    )
                    records[(m_name, m_ver)] = demoted_item
                    self._log_audit(
                        tenant_id=tenant_id,
                        model_name=m_name,
                        model_version=m_ver,
                        action="DEMOTE_PREVIOUS_PRODUCTION",
                        previous_state=ModelLifecycleState.PRODUCTION,
                        new_state=ModelLifecycleState.DEPRECATED,
                    )

        updated_manifest = manifest.model_copy(
            update={
                "lifecycle_state": updated_rec.lifecycle_state,
                "updated_at": datetime.now(UTC),
            }
        )

        records[(model_name, model_version)] = updated_manifest
        self._log_audit(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            action="PROMOTE_PRODUCTION",
            previous_state=current_state,
            new_state=ModelLifecycleState.PRODUCTION,
        )

        logger.info(
            "Promoted model %s:v%s to PRODUCTION for tenant %s",
            model_name,
            model_version,
            tenant_id,
        )

        return updated_manifest

    def deprecate_model(
        self, tenant_id: uuid.UUID, model_name: str, model_version: str
    ) -> RegisteredModelManifest:
        """Deprecate model version (Phase 245)."""
        manifest = self.get_model(tenant_id, model_name, model_version)
        current_state = manifest.lifecycle_state

        ver_rec = ModelVersionRecord(
            model_id=manifest.artifact_manifest.model_id,
            model_version=manifest.model_version,
            model_name=manifest.model_name,
            tenant_id=tenant_id,
            lifecycle_state=current_state,
            artifact_checksum=manifest.artifact_manifest.checksum,
            dataset_fingerprint=manifest.evaluation_manifest.dataset_fingerprint,
            feature_versions=manifest.evaluation_manifest.feature_versions,
            training_run_id=manifest.artifact_manifest.training_run_id,
            configuration_hash=manifest.evaluation_manifest.configuration_hash,
        )

        updated_rec = self.version_manager.transition_state(ver_rec, ModelLifecycleState.DEPRECATED)
        updated_manifest = manifest.model_copy(
            update={
                "lifecycle_state": updated_rec.lifecycle_state,
                "updated_at": datetime.now(UTC),
            }
        )

        self._records[tenant_id][(model_name, model_version)] = updated_manifest
        self._log_audit(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            action="DEPRECATE",
            previous_state=current_state,
            new_state=ModelLifecycleState.DEPRECATED,
        )

        return updated_manifest

    def retire_model(
        self, tenant_id: uuid.UUID, model_name: str, model_version: str
    ) -> RegisteredModelManifest:
        """Retire model version into terminal state (Phase 245)."""
        manifest = self.get_model(tenant_id, model_name, model_version)
        current_state = manifest.lifecycle_state

        ver_rec = ModelVersionRecord(
            model_id=manifest.artifact_manifest.model_id,
            model_version=manifest.model_version,
            model_name=manifest.model_name,
            tenant_id=tenant_id,
            lifecycle_state=current_state,
            artifact_checksum=manifest.artifact_manifest.checksum,
            dataset_fingerprint=manifest.evaluation_manifest.dataset_fingerprint,
            feature_versions=manifest.evaluation_manifest.feature_versions,
            training_run_id=manifest.artifact_manifest.training_run_id,
            configuration_hash=manifest.evaluation_manifest.configuration_hash,
        )

        updated_rec = self.version_manager.transition_state(ver_rec, ModelLifecycleState.RETIRED)
        updated_manifest = manifest.model_copy(
            update={
                "lifecycle_state": updated_rec.lifecycle_state,
                "updated_at": datetime.now(UTC),
            }
        )

        self._records[tenant_id][(model_name, model_version)] = updated_manifest
        self._log_audit(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=model_version,
            action="RETIRE",
            previous_state=current_state,
            new_state=ModelLifecycleState.RETIRED,
        )

        return updated_manifest

    def resolve_production_model(
        self, tenant_id: uuid.UUID, model_name: str
    ) -> RegisteredModelManifest:
        """Resolve active PRODUCTION model version for tenant (Phase 245)."""
        records = self._get_tenant_records(tenant_id)
        for (m_name, _), item in records.items():
            if m_name == model_name and item.lifecycle_state == ModelLifecycleState.PRODUCTION:
                return item

        raise ValueError(
            f"No active PRODUCTION model found for model '{model_name}' under tenant {tenant_id}."
        )

    def rollback_production_model(
        self, tenant_id: uuid.UUID, model_name: str, target_version: str
    ) -> RegisteredModelManifest:
        """Rollback active production model to a target registered version (Phase 245)."""
        target_manifest = self.get_model(tenant_id, model_name, target_version)
        if target_manifest.lifecycle_state == ModelLifecycleState.RETIRED:
            raise ValueError(
                f"Cannot rollback to RETIRED model version '{target_version}'! Model is retired permanently."  # noqa: E501
            )

        # Demote current production model if any
        records = self._get_tenant_records(tenant_id)
        for (m_name, m_ver), item in list(records.items()):
            if m_name == model_name and item.lifecycle_state == ModelLifecycleState.PRODUCTION:
                demoted_item = item.model_copy(
                    update={
                        "lifecycle_state": ModelLifecycleState.DEPRECATED,
                        "updated_at": datetime.now(UTC),
                    }
                )
                records[(m_name, m_ver)] = demoted_item

        current_state = target_manifest.lifecycle_state
        updated_target = target_manifest.model_copy(
            update={
                "lifecycle_state": ModelLifecycleState.PRODUCTION,
                "updated_at": datetime.now(UTC),
            }
        )
        records[(model_name, target_version)] = updated_target

        self._log_audit(
            tenant_id=tenant_id,
            model_name=model_name,
            model_version=target_version,
            action="ROLLBACK_PRODUCTION",
            previous_state=current_state,
            new_state=ModelLifecycleState.PRODUCTION,
        )

        return updated_target

    def verify_model_artifact(
        self, tenant_id: uuid.UUID, model_name: str, model_version: str
    ) -> bool:
        """Verify artifact checksum integrity against stored registry manifest (Phase 245)."""
        manifest = self.get_model(tenant_id, model_name, model_version)
        artifacts = self._get_tenant_artifacts(tenant_id)
        key = (model_name, model_version)
        raw_bytes = artifacts.get(key)
        if not raw_bytes:
            return False

        return self.serializer.verify_checksum(raw_bytes, manifest.artifact_manifest)

    def get_audit_trail(self, tenant_id: uuid.UUID) -> list[RegistryAuditRecord]:
        """Get immutable audit logs for tenant model operations (Phase 245)."""
        return list(self._get_tenant_audit(tenant_id))
