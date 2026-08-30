"""Unit tests for Model Versioning & Lifecycle State Transitions (Phase 244)."""

from __future__ import annotations

import uuid

import pytest

from app.ml.versioning.model_version_manager import ModelVersionManager
from app.schemas.ml_versioning import ModelLifecycleState, ModelVersionRecord


def test_01_semver_validation_and_valid_lifecycle_transitions() -> None:
    """1. Test SemVer pattern enforcement and valid lifecycle state transitions."""
    manager = ModelVersionManager()
    t_id = uuid.uuid4()

    record = ModelVersionRecord(
        model_id="fraudguard_xgb",
        model_version="1.0.0",
        tenant_id=t_id,
        lifecycle_state=ModelLifecycleState.REGISTERED,
        artifact_checksum="a" * 64,
        dataset_fingerprint="b" * 64,
        feature_versions={"feat_a": "1.0.0"},
        training_run_id=uuid.uuid4(),
        configuration_hash="c" * 64,
    )

    # Valid SemVer check
    assert record.model_version == "1.0.0"

    # REGISTERED -> STAGING
    rec_staging = manager.transition_state(record, ModelLifecycleState.STAGING)
    assert rec_staging.lifecycle_state == ModelLifecycleState.STAGING

    # STAGING -> PRODUCTION
    rec_prod = manager.transition_state(rec_staging, ModelLifecycleState.PRODUCTION)
    assert rec_prod.lifecycle_state == ModelLifecycleState.PRODUCTION

    # PRODUCTION -> DEPRECATED
    rec_dep = manager.transition_state(rec_prod, ModelLifecycleState.DEPRECATED)
    assert rec_dep.lifecycle_state == ModelLifecycleState.DEPRECATED

    # DEPRECATED -> RETIRED
    rec_ret = manager.transition_state(rec_dep, ModelLifecycleState.RETIRED)
    assert rec_ret.lifecycle_state == ModelLifecycleState.RETIRED


def test_02_invalid_semver_and_forbidden_state_transitions() -> None:
    """2. Test that invalid SemVer and forbidden state transitions fail closed."""
    t_id = uuid.uuid4()

    # Invalid SemVer pattern
    with pytest.raises(ValueError, match="must satisfy SemVer pattern"):
        ModelVersionRecord(
            model_id="fraudguard_xgb",
            model_version="v1.0",
            tenant_id=t_id,
            artifact_checksum="a" * 64,
            dataset_fingerprint="b" * 64,
            feature_versions={"feat_a": "1.0.0"},
            training_run_id=uuid.uuid4(),
            configuration_hash="c" * 64,
        )

    manager = ModelVersionManager()
    retired_record = ModelVersionRecord(
        model_id="fraudguard_xgb",
        model_version="1.0.0",
        tenant_id=t_id,
        lifecycle_state=ModelLifecycleState.RETIRED,
        artifact_checksum="a" * 64,
        dataset_fingerprint="b" * 64,
        feature_versions={"feat_a": "1.0.0"},
        training_run_id=uuid.uuid4(),
        configuration_hash="c" * 64,
    )

    # RETIRED -> PRODUCTION must fail closed!
    with pytest.raises(ValueError, match="Forbidden state transition"):
        manager.transition_state(retired_record, ModelLifecycleState.PRODUCTION)
