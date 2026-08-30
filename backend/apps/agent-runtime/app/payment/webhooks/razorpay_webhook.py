"""Razorpay Webhook Handler Boundary (Phase 293)."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from typing import Any

from app.payment.webhooks.razorpay_signature import RazorpayWebhookSignatureVerifier
from app.schemas.payment_webhook import (
    UntrustedWebhookRequest,
    VerifiedWebhookEnvelope,
    WebhookIngestionOutcome,
    WebhookIngestionResult,
)

logger = logging.getLogger("agentpay.payment.webhooks.handler")


class WebhookReplayTracker:
    """Thread-safe in-memory replay defense tracker abstraction (Phase 293)."""

    def __init__(self, max_capacity: int = 10000) -> None:
        self._seen_keys: set[str] = set()
        self._lock = threading.Lock()
        self._max_capacity = max_capacity

    def is_duplicate(self, event_id: str | None, payload_fingerprint: str) -> bool:
        """Check and record event identity to detect duplicate webhook replays."""
        key = f"evt:{event_id}" if event_id else f"fp:{payload_fingerprint}"
        with self._lock:
            if key in self._seen_keys:
                return True
            if len(self._seen_keys) >= self._max_capacity:
                # Evict half if capacity is reached
                self._seen_keys.clear()
            self._seen_keys.add(key)
            return False


class RazorpayWebhookHandler:
    """Production Razorpay Webhook Ingestion Boundary (Phase 293).

    Primary responsibility: Safely ingest raw webhook requests, invoke Phase 294 signature
    verification, parse JSON ONLY post-verification, perform replay detection, and construct
    a trusted VerifiedWebhookEnvelope.

    CRITICAL SAFETY RULES:
    1. Signature verification occurs BEFORE any JSON parsing or event object creation.
    2. Fails closed on any signature mismatch or invalid format.
    3. DOES NOT mutate payment status (Phase 295 responsibility).
    4. DOES NOT execute Phase 295 event processing.
    """

    def __init__(
        self,
        verifier: RazorpayWebhookSignatureVerifier | None = None,
        replay_tracker: WebhookReplayTracker | None = None,
        event_processor: Any | None = None,
    ) -> None:
        self.verifier = verifier or RazorpayWebhookSignatureVerifier()
        self.replay_tracker = replay_tracker or WebhookReplayTracker()
        self.event_processor = event_processor

    def process_webhook(
        self, request: UntrustedWebhookRequest
    ) -> tuple[WebhookIngestionResult, VerifiedWebhookEnvelope | None]:
        """Ingest untrusted webhook payload and verify cryptographic signature.

        Returns (WebhookIngestionResult, VerifiedWebhookEnvelope | None).
        If verification fails, returns (failed_result, None).
        """
        payload_fingerprint = hashlib.sha256(request.raw_body or b"").hexdigest()

        # 1. Cryptographic Signature Verification BEFORE JSON Parsing (Phase 294)
        ver_result = self.verifier.verify_signature(
            raw_body=request.raw_body,
            signature=request.signature,
            tenant_id=request.tenant_id,
        )

        if not ver_result.verified:
            logger.warning(
                "Webhook ingestion REJECTED: Signature verification failed (%s)",
                ver_result.reason_code,
            )
            return (
                WebhookIngestionResult(
                    outcome=WebhookIngestionOutcome.INVALID_SIGNATURE,
                    status_code=401,
                    message=(
                        f"Cryptographic signature verification failed: {ver_result.reason_code}"
                    ),
                    payload_fingerprint=payload_fingerprint,
                ),
                None,
            )

        # 2. Parse Raw Bytes as JSON ONLY AFTER Signature Verification
        try:
            raw_json: dict[str, Any] = json.loads(request.raw_body.decode("utf-8"))
            if not isinstance(raw_json, dict):
                raise ValueError("Parsed JSON payload is not a dict.")
        except Exception as err:
            logger.warning("Webhook ingestion REJECTED: Malformed JSON (%s)", type(err).__name__)
            return (
                WebhookIngestionResult(
                    outcome=WebhookIngestionOutcome.MALFORMED_PAYLOAD,
                    status_code=400,
                    message="Malformed JSON webhook body.",
                    payload_fingerprint=payload_fingerprint,
                ),
                None,
            )

        # 3. Extract Provider Event Identity & Metadata
        # Razorpay webhooks contain "event" and optionally "event_id" or "id"
        event_type = str(raw_json.get("event", "unknown.event"))
        event_id = raw_json.get("event_id") or raw_json.get("id")
        if event_id is not None:
            event_id = str(event_id).strip()

        # 4. Replay Defense Check
        if self.replay_tracker.is_duplicate(event_id, payload_fingerprint):
            logger.info(
                "Webhook ingestion IDEMPOTENT: Duplicate event detected (event_id=%s)", event_id
            )
            return (
                WebhookIngestionResult(
                    outcome=WebhookIngestionOutcome.DUPLICATE,
                    status_code=200,
                    message="Duplicate webhook event received; ignored idempotently.",
                    event_id=event_id,
                    event_type=event_type,
                    payload_fingerprint=payload_fingerprint,
                ),
                None,
            )

        # 5. Environment Context Resolution
        environment = request.environment or "production"

        # 6. Construct Safe VerifiedWebhookEnvelope
        envelope = VerifiedWebhookEnvelope(
            provider="razorpay",
            event_id=event_id,
            event_type=event_type,
            tenant_id=request.tenant_id,
            environment=environment,
            verification_status="VERIFIED",
            signature_algorithm="HMAC-SHA256",
            payload_fingerprint=payload_fingerprint,
            raw_payload_digest=payload_fingerprint,
            verified=True,
            payload=raw_json,
        )

        logger.info(
            "Webhook ingestion ACCEPTED & VERIFIED (event_type=%s, event_id=%s, fingerprint=%s...)",
            event_type,
            event_id,
            payload_fingerprint[:12],
        )

        # Note: Phase 295 event processing is NOT executed here per architectural rules.

        return (
            WebhookIngestionResult(
                outcome=WebhookIngestionOutcome.ACCEPTED,
                status_code=200,
                message="Webhook ingested and cryptographically verified successfully.",
                event_id=event_id,
                event_type=event_type,
                payload_fingerprint=payload_fingerprint,
            ),
            envelope,
        )
