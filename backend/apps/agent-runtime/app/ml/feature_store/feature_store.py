"""Production Feature Store Registry & Management Foundation (Phase 230)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from app.ml.config.ml_config import MLPipelineConfig, get_default_ml_config
from app.ml.features.base import FeatureDefinition
from app.schemas.ml_features import FeatureLineageGraphNode, FeatureStoreRecord

logger = logging.getLogger("fraudguard.ml.feature_store")


class FeatureStore:
    """Production Feature Registry, Lineage & Store Management Engine (Phase 230)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()
        self._registry: dict[str, FeatureStoreRecord] = {}
        self._lineage: dict[str, FeatureLineageGraphNode] = {}

    def register_feature(
        self,
        definition: FeatureDefinition,
        status: str = "ACTIVE",
        attributes: dict[str, Any] | None = None,
    ) -> FeatureStoreRecord:
        """Register an immutable feature version in the Feature Store Registry (Phase 230)."""
        now = datetime.now(UTC)
        fid = definition.feature_id or f"{definition.name}:{definition.version}"

        record = FeatureStoreRecord(
            feature_id=fid,
            name=definition.name,
            feature_type=definition.feature_type.value,
            category=definition.category.value,
            security_classification=definition.security_classification.value,
            source=definition.source,
            version=definition.version,
            status=status,
            description=definition.description or definition.transformation_description,
            freshness_seconds=definition.freshness_seconds,
            registered_at=now,
            updated_at=now,
            attributes=attributes or {},
        )
        self._registry[fid] = record
        self._lineage[definition.name] = FeatureLineageGraphNode(
            feature_name=definition.name,
            source=definition.source,
            dataset_version=self.config.dataset_version,
            dependencies=definition.dependencies,
        )
        logger.info(
            "Registered immutable feature '%s' (ID: %s, status=%s) in Feature Store",
            definition.name,
            fid,
            status,
        )
        return record

    def get_feature_record(
        self, feature_name: str, version: str = "1.0.0"
    ) -> FeatureStoreRecord | None:  # noqa: E501
        """Lookup a registered feature record by name and version (Phase 230)."""
        fid = f"{feature_name}:{version}"
        return self._registry.get(fid) or self._registry.get(feature_name)

    def update_feature_status(
        self, feature_name: str, new_status: str, version: str = "1.0.0"
    ) -> FeatureStoreRecord:
        """Update lifecycle status of a feature version (DRAFT -> VALIDATING -> ACTIVE -> DEPRECATED -> RETIRED)."""  # noqa: E501
        valid_statuses = {"DRAFT", "VALIDATING", "ACTIVE", "DEPRECATED", "RETIRED"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {valid_statuses}")

        fid = f"{feature_name}:{version}"
        record = self._registry.get(fid) or self._registry.get(feature_name)
        if not record:
            raise KeyError(f"Feature '{feature_name}' (v{version}) not found in registry.")

        # Transition validation
        if record.status == "RETIRED" and new_status == "ACTIVE":
            raise ValueError("Cannot directly activate RETIRED feature; register a new version.")

        updated_record = FeatureStoreRecord(
            feature_id=record.feature_id,
            name=record.name,
            feature_type=record.feature_type,
            category=record.category,
            security_classification=record.security_classification,
            source=record.source,
            version=record.version,
            status=new_status,
            description=record.description,
            freshness_seconds=record.freshness_seconds,
            registered_at=record.registered_at,
            updated_at=datetime.now(UTC),
            attributes=record.attributes,
        )
        self._registry[record.feature_id] = updated_record
        logger.info("Updated feature '%s' (v%s) status to %s", feature_name, version, new_status)
        return updated_record

    def list_active_features(self) -> list[FeatureStoreRecord]:
        """List all active features in the Feature Store (Phase 230)."""
        return [r for r in self._registry.values() if r.status == "ACTIVE"]

    def export_catalog(self) -> dict[str, Any]:
        """Export feature catalog summary and lineage metadata (Phase 230)."""
        return {
            "total_features": len(self._registry),
            "active_features": len(self.list_active_features()),
            "catalog_version": self.config.feature_pipeline_version,
            "lineage_nodes": {k: v.model_dump() for k, v in self._lineage.items()},
            "features": {k: v.model_dump() for k, v in self._registry.items()},
        }
