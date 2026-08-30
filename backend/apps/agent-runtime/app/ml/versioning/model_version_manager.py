"""Model Version Manager with Lifecycle State Transitions (Phase 244)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.schemas.ml_versioning import (
    VALID_STATE_TRANSITIONS,
    ModelLifecycleState,
    ModelVersionRecord,
)

logger = logging.getLogger("fraudguard.ml.versioning")


class ModelVersionManager:
    """Production Model Version Manager enforcing SemVer Immutability & Lifecycle Rules (Phase 244)."""  # noqa: E501

    def transition_state(
        self,
        record: ModelVersionRecord,
        new_state: str,
    ) -> ModelVersionRecord:
        """Transition model version record to new lifecycle state (Phase 244)."""
        current_state = record.lifecycle_state

        if new_state not in ModelLifecycleState.ALL_STATES:
            raise ValueError(f"Invalid target state '{new_state}'.")

        allowed_next = VALID_STATE_TRANSITIONS.get(current_state, set())

        if new_state not in allowed_next:
            logger.error(
                "Forbidden state transition: %s -> %s for model %s v%s",
                current_state,
                new_state,
                record.model_id,
                record.model_version,
            )
            raise ValueError(
                f"Forbidden state transition: '{current_state}' -> '{new_state}' for model {record.model_id} v{record.model_version}!"  # noqa: E501
            )

        updated_record = record.model_copy(
            update={
                "lifecycle_state": new_state,
                "updated_at": datetime.now(UTC),
            }
        )

        logger.info(
            "Model %s v%s state transitioned: %s -> %s",
            record.model_id,
            record.model_version,
            current_state,
            new_state,
        )

        return updated_record
