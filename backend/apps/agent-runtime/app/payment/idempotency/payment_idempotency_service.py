"""Payment Idempotency Subsystem (Phase 297)."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.schemas.payment_idempotency import IdempotencyState, PaymentIdempotencyRecord

logger = logging.getLogger("agentpay.payment.idempotency")


class PaymentIdempotencyError(Exception):
    """Domain exception for payment idempotency errors."""

    def __init__(self, message: str, error_code: str = "IDEMPOTENCY_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class PaymentIdempotencyConflictError(PaymentIdempotencyError):
    """Exception raised when an idempotency key is reused with a different request fingerprint."""

    def __init__(
        self,
        message: str = "Idempotency key reused with a different request fingerprint.",
        error_code: str = "IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


class PaymentIdempotencyService:
    """Production Payment Idempotency Engine (Phase 297).

    Primary responsibility: Enforce multi-tenant idempotency identity binding and request
    fingerprinting to prevent duplicate payment operations or duplicate financial side effects.

    Executes BEFORE external financial calls (Razorpay provider order creation).
    Thread-safe concurrency protection isolated behind an abstract interface.
    """

    def __init__(self, max_capacity: int = 10000) -> None:
        self._store: dict[str, PaymentIdempotencyRecord] = {}
        self._record_id_map: dict[uuid.UUID, str] = {}
        self._lock = threading.Lock()
        self._max_capacity = max_capacity

    def compute_identity_hash(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        operation: str,
        idempotency_key: str,
    ) -> str:
        """Compute canonical SHA-256 idempotency identity hash."""
        clean_key = (idempotency_key or "").strip()
        if not clean_key:
            raise PaymentIdempotencyError(
                "Idempotency key cannot be empty.", error_code="INVALID_IDEMPOTENCY_KEY"
            )

        identity_str = (
            f"{str(tenant_id).lower()}|{str(agent_id).lower()}|"
            f"{transaction_id.strip()}|{operation.strip()}|{clean_key}"
        )
        return hashlib.sha256(identity_str.encode("utf-8")).hexdigest()

    def compute_request_fingerprint(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        operation: str,
        request_params: dict[str, Any],
    ) -> str:
        """Compute canonical SHA-256 fingerprint over request parameters (NO secrets)."""
        canonical_params = {
            "tenant_id": str(tenant_id),
            "agent_id": str(agent_id),
            "transaction_id": transaction_id,
            "operation": operation,
            "params": {
                k: (str(v) if isinstance(v, (uuid.UUID, Decimal)) else v)
                for k, v in sorted(request_params.items())
                if k not in {"key_secret", "webhook_secret", "authorization_header"}
            },
        }
        encoded = json.dumps(canonical_params, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def reserve_idempotency(
        self,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        operation: str,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> tuple[PaymentIdempotencyRecord, bool]:
        """Reserve or retrieve idempotency record BEFORE external financial call.

        Returns (record, is_new).
        If is_new is True -> caller must execute the provider operation.
        If is_new is False and state is COMPLETED -> caller must return safe_result_payload.
        If state is IN_PROGRESS -> concurrency collision!
        If request_fingerprint differs -> raises PaymentIdempotencyConflictError (409)!
        """
        identity_hash = self.compute_identity_hash(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            operation=operation,
            idempotency_key=idempotency_key,
        )

        with self._lock:
            existing = self._store.get(identity_hash)

            if existing is None:
                # Capacity eviction if needed
                if len(self._store) >= self._max_capacity:
                    # Clear half
                    keys_to_clear = list(self._store.keys())[: self._max_capacity // 2]
                    for k in keys_to_clear:
                        old_rec = self._store.pop(k, None)
                        if old_rec:
                            self._record_id_map.pop(old_rec.record_id, None)

                new_record = PaymentIdempotencyRecord(
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    transaction_id=transaction_id,
                    operation=operation,
                    idempotency_key=idempotency_key.strip(),
                    idempotency_identity_hash=identity_hash,
                    request_fingerprint=request_fingerprint,
                    state=IdempotencyState.IN_PROGRESS,
                )
                self._store[identity_hash] = new_record
                self._record_id_map[new_record.record_id] = identity_hash

                logger.info(
                    "Idempotency RESERVED [op=%s, key=%s, hash=%s...]",
                    operation,
                    idempotency_key[:8],
                    identity_hash[:12],
                )
                return (new_record, True)

            # Check Request Fingerprint Integrity
            if existing.request_fingerprint != request_fingerprint:
                msg = (
                    f"Idempotency key '{idempotency_key}' reused with a different "
                    f"request fingerprint! Tenant: {tenant_id}, Transaction: {transaction_id}."
                )
                logger.warning("Idempotency CONFLICT: %s", msg)
                raise PaymentIdempotencyConflictError(message=msg)

            logger.info(
                "Idempotency REPLAY DETECTED [op=%s, state=%s, key=%s]",
                operation,
                existing.state.value,
                idempotency_key[:8],
            )
            return (existing, False)

    def complete_idempotency(
        self,
        record_id: uuid.UUID,
        safe_result_payload: dict[str, Any],
    ) -> PaymentIdempotencyRecord:
        """Mark idempotency record as COMPLETED and store safe result payload."""
        with self._lock:
            hash_key = self._record_id_map.get(record_id)
            if not hash_key or hash_key not in self._store:
                raise PaymentIdempotencyError("Idempotency record not found for completion.")

            existing = self._store[hash_key]

            # Redact any accidental secret keys from payload
            clean_payload = {
                k: v
                for k, v in safe_result_payload.items()
                if k not in {"key_secret", "webhook_secret"}
            }

            updated = PaymentIdempotencyRecord(
                record_id=existing.record_id,
                tenant_id=existing.tenant_id,
                agent_id=existing.agent_id,
                transaction_id=existing.transaction_id,
                operation=existing.operation,
                idempotency_key=existing.idempotency_key,
                idempotency_identity_hash=existing.idempotency_identity_hash,
                request_fingerprint=existing.request_fingerprint,
                state=IdempotencyState.COMPLETED,
                safe_result_payload=clean_payload,
                created_at=existing.created_at,
                completed_at=datetime.now(UTC),
            )
            self._store[hash_key] = updated

            logger.info(
                "Idempotency COMPLETED [op=%s, key=%s]",
                existing.operation,
                existing.idempotency_key[:8],
            )
            return updated

    def fail_idempotency(
        self,
        record_id: uuid.UUID,
        error_code: str = "OPERATION_FAILED",
    ) -> PaymentIdempotencyRecord:
        """Mark idempotency record as FAILED."""
        with self._lock:
            hash_key = self._record_id_map.get(record_id)
            if not hash_key or hash_key not in self._store:
                raise PaymentIdempotencyError("Idempotency record not found for failure update.")

            existing = self._store[hash_key]

            updated = PaymentIdempotencyRecord(
                record_id=existing.record_id,
                tenant_id=existing.tenant_id,
                agent_id=existing.agent_id,
                transaction_id=existing.transaction_id,
                operation=existing.operation,
                idempotency_key=existing.idempotency_key,
                idempotency_identity_hash=existing.idempotency_identity_hash,
                request_fingerprint=existing.request_fingerprint,
                state=IdempotencyState.FAILED,
                error_code=error_code,
                created_at=existing.created_at,
                completed_at=datetime.now(UTC),
            )
            self._store[hash_key] = updated

            logger.warning(
                "Idempotency FAILED [op=%s, key=%s, code=%s]",
                existing.operation,
                existing.idempotency_key[:8],
                error_code,
            )
            return updated

    async def reserve_idempotency_db(
        self,
        db_session: Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        transaction_id: str,
        operation: str,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> tuple[PaymentIdempotencyRecord, bool]:
        """Reserve or retrieve idempotency record using PostgreSQL SELECT ... FOR UPDATE database lock (P1-01).

        Guarantees multi-worker / multi-container correctness across processes.
        """
        from sqlalchemy import select

        from app.infrastructure.database.models.payment_idempotency_key import PaymentIdempotencyKey

        identity_hash = self.compute_identity_hash(
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            operation=operation,
            idempotency_key=idempotency_key,
        )

        stmt = (
            select(PaymentIdempotencyKey)
            .where(
                PaymentIdempotencyKey.tenant_id == tenant_id,
                PaymentIdempotencyKey.idempotency_key == idempotency_key.strip(),
            )
            .with_for_update()
        )

        res = await db_session.execute(stmt)
        db_key = res.scalar_one_or_none()

        if db_key is None:
            new_db_key = PaymentIdempotencyKey(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                idempotency_key=idempotency_key.strip(),
                operation_type=(
                    operation.lower()
                    if operation.lower()
                    in {
                        "create_order",
                        "authorize",
                        "capture",
                        "refund",
                        "cancel",
                        "payment",
                        "retry",
                        "webhook",
                    }
                    else "payment"
                ),
                status="processing",
                request_id=transaction_id,
            )
            db_session.add(new_db_key)
            await db_session.flush()

            record = PaymentIdempotencyRecord(
                record_id=new_db_key.id,
                tenant_id=tenant_id,
                agent_id=agent_id,
                transaction_id=transaction_id,
                operation=operation,
                idempotency_key=idempotency_key.strip(),
                idempotency_identity_hash=identity_hash,
                request_fingerprint=request_fingerprint,
                state=IdempotencyState.IN_PROGRESS,
            )
            return (record, True)

        # Existing record found in DB
        existing_record = PaymentIdempotencyRecord(
            record_id=db_key.id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=transaction_id,
            operation=operation,
            idempotency_key=idempotency_key.strip(),
            idempotency_identity_hash=identity_hash,
            request_fingerprint=request_fingerprint,
            state=(
                IdempotencyState.COMPLETED
                if db_key.status == "completed"
                else (
                    IdempotencyState.FAILED
                    if db_key.status == "failed"
                    else IdempotencyState.IN_PROGRESS
                )
            ),
            safe_result_payload=db_key.response_payload or {},
        )

        if request_fingerprint and existing_record.request_fingerprint != request_fingerprint:
            raise PaymentIdempotencyConflictError(
                f"Idempotency key '{idempotency_key}' reused with a different request fingerprint!"
            )

        return (existing_record, False)
