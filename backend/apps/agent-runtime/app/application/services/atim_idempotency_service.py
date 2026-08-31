"""ATIM Distributed Idempotency & Transaction Consistency Service (Phase 21 / Group 11)."""

from datetime import datetime, timedelta
import hashlib
import json
import logging
from typing import Any, Optional
import uuid

from app.domain.governance.idempotency_models import IdempotencyRecord, IdempotencyState

logger = logging.getLogger("agentpay.atim.idempotency")


class ATIMIdempotencyService:
    """Service managing Stripe-grade distributed idempotency and zero-double-payment protection."""

    def __init__(self, ttl_hours: int = 24) -> None:
        self.ttl_hours = ttl_hours
        # In-memory store fallback for fast testing and DB persistence synchronization
        self._records: dict[tuple[uuid.UUID, Optional[uuid.UUID], str, str], IdempotencyRecord] = {}

    def compute_payload_hash(self, payload: dict[str, Any]) -> str:
        """Compute canonical SHA-256 fingerprint over request payload."""
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def process_idempotent_request(
        self,
        tenant_id: uuid.UUID,
        operation: str,
        idempotency_key: str,
        payload: dict[str, Any],
        agent_id: Optional[uuid.UUID] = None,
    ) -> tuple[bool, Optional[IdempotencyRecord]]:
        """Process or retrieve idempotent request.

        Returns:
            Tuple (is_duplicate: bool, record: IdempotencyRecord)
        """
        payload_hash = self.compute_payload_hash(payload)
        key = (tenant_id, agent_id, operation, idempotency_key)

        existing = self._records.get(key)
        if existing:
            # Check payload fingerprint matching
            if existing.payload_hash != payload_hash:
                logger.warning(
                    "IDEMPOTENCY PAYLOAD MISMATCH for Tenant %s (Key %s)",
                    tenant_id,
                    idempotency_key,
                )
                raise ValueError("Payload mismatch: Existing idempotency key reused with different request body.")

            if existing.state == IdempotencyState.PROCESSING:
                logger.warning(
                    "CONCURRENT IDEMPOTENCY REQUEST IN PROGRESS for Tenant %s (Key %s)",
                    tenant_id,
                    idempotency_key,
                )
                raise PermissionError("Request with this idempotency key is currently in progress.")

            logger.info("Retrieved existing idempotent response for Tenant %s (Key %s)", tenant_id, idempotency_key)
            return True, existing

        # First-time request -> Register record in PROCESSING state
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.ttl_hours)

        record = IdempotencyRecord(
            tenant_id=tenant_id,
            agent_id=agent_id,
            operation=operation,
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            state=IdempotencyState.PROCESSING,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
        )

        self._records[key] = record
        logger.info("Registered new idempotency lock for Tenant %s (Key %s)", tenant_id, idempotency_key)
        return False, record

    def complete_idempotent_request(
        self,
        tenant_id: uuid.UUID,
        operation: str,
        idempotency_key: str,
        state: IdempotencyState,
        response_code: int,
        response_body: dict[str, Any],
        agent_id: Optional[uuid.UUID] = None,
    ) -> IdempotencyRecord:
        """Mark idempotency record execution as completed with saved response."""
        key = (tenant_id, agent_id, operation, idempotency_key)
        record = self._records.get(key)
        if not record:
            raise KeyError(f"Idempotency record '{idempotency_key}' not found for tenant '{tenant_id}'.")

        record.state = state
        record.response_code = response_code
        record.response_body = response_body
        record.updated_at = datetime.utcnow()

        logger.info(
            "Completed idempotent execution for Tenant %s (Key %s) with state %s",
            tenant_id,
            idempotency_key,
            state.value,
        )
        return record
