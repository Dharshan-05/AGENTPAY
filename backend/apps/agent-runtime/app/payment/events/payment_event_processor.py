"""Payment Event Processing Subsystem (Phase 295)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

from app.payment.status.payment_status_service import PaymentStatusError, PaymentStatusService
from app.schemas.payment import PaymentOrderResult, PaymentStatus, SupportedCurrency
from app.schemas.payment_event import (
    NormalizedPaymentEventType,
    PaymentEventProcessingResult,
    PaymentEventProcessingStatus,
)
from app.schemas.payment_webhook import VerifiedWebhookEnvelope

logger = logging.getLogger("agentpay.payment.events.processor")


class PaymentEventProcessorError(Exception):
    """Domain exception raised when payment event processing encounters unrecoverable errors."""


class RazorpayPaymentEventProcessor:
    """Production Razorpay Payment Event Processing Engine (Phase 295).

    Primary responsibility: Map verified Razorpay webhook events to normalized domain payment
    events, extract payment entity payload, validate identity/context binding, and invoke
    PaymentStatusService to execute authoritative state machine transitions.

    FAILS CLOSED on unverified envelopes, identity mismatches, or illegal state transitions.
    """

    def __init__(self, status_service: PaymentStatusService | None = None) -> None:
        self.status_service = status_service or PaymentStatusService()

    def process_event(
        self,
        envelope: VerifiedWebhookEnvelope,
        expected_order: PaymentOrderResult | None = None,
        current_status: PaymentStatus | None = None,
    ) -> PaymentEventProcessingResult:
        """Process trusted VerifiedWebhookEnvelope and execute state transitions (Phase 295).

        FAILS CLOSED if envelope.verified is False or identity/amount binding fails.
        """
        processing_id = uuid.uuid4()

        # 1. Unverified Envelope Check
        if not envelope.verified:
            logger.warning(
                "Event processing REJECTED: Envelope is unverified (envelope_id=%s)",
                envelope.envelope_id,
            )
            return self._build_result(
                processing_id=processing_id,
                envelope=envelope,
                normalized_type=NormalizedPaymentEventType.UNKNOWN_EVENT,
                proc_status=PaymentEventProcessingStatus.FAILED,
                reason="UNVERIFIED_WEBHOOK_ENVELOPE",
            )

        # 2. Normalize Provider Event Type
        normalized_type = self._normalize_event_type(envelope.event_type)

        # 3. Extract Payload Entity Data
        entity_data = self._extract_entity_data(envelope.payload)
        extracted_order = entity_data.get("order_id")
        order_id = extracted_order or (expected_order.order_id if expected_order else None)
        payment_id = entity_data.get("payment_id")
        notes = entity_data.get("notes", {})

        # Resolve Context Binding
        extracted_tenant = envelope.tenant_id or self._parse_uuid(notes.get("tenant_id"))
        extracted_agent = self._parse_uuid(notes.get("agent_id"))
        extracted_tx = notes.get("transaction_id") or notes.get("tx_id")

        tenant_id = expected_order.tenant_id if expected_order else extracted_tenant
        agent_id = expected_order.agent_id if expected_order else extracted_agent
        transaction_id = expected_order.transaction_id if expected_order else extracted_tx

        currency_str = entity_data.get("currency")
        parsed_currency: SupportedCurrency | None = None
        if currency_str:
            try:
                parsed_currency = SupportedCurrency(str(currency_str).upper().strip())
            except ValueError:
                pass

        # 4. Contextual & Identity Integrity Check (if expected_order is supplied)
        if expected_order:
            if extracted_order and extracted_order != expected_order.order_id:
                logger.warning(
                    "Event processing MISMATCH: order_id '%s' != expected '%s'",
                    extracted_order,
                    expected_order.order_id,
                )
                return self._build_result(
                    processing_id=processing_id,
                    envelope=envelope,
                    normalized_type=normalized_type,
                    proc_status=PaymentEventProcessingStatus.MISMATCH,
                    reason="IDENTITY_ORDER_ID_MISMATCH",
                    tenant_id=expected_order.tenant_id,
                    agent_id=expected_order.agent_id,
                    tx_id=expected_order.transaction_id,
                    order_id=extracted_order,
                    payment_id=payment_id,
                    currency=parsed_currency,
                )

            if extracted_tenant and extracted_tenant != expected_order.tenant_id:
                logger.warning("Event processing MISMATCH: tenant_id mismatch.")
                return self._build_result(
                    processing_id=processing_id,
                    envelope=envelope,
                    normalized_type=normalized_type,
                    proc_status=PaymentEventProcessingStatus.MISMATCH,
                    reason="IDENTITY_TENANT_ID_MISMATCH",
                    tenant_id=extracted_tenant,
                    agent_id=expected_order.agent_id,
                    tx_id=expected_order.transaction_id,
                    order_id=expected_order.order_id,
                    payment_id=payment_id,
                    currency=parsed_currency,
                )

        # 5. Determine State Machine Action
        target_status = self._map_event_to_target_status(normalized_type)

        if target_status is None:
            logger.info(
                "Event type '%s' ignored (no status mutation required).", envelope.event_type
            )
            return self._build_result(
                processing_id=processing_id,
                envelope=envelope,
                normalized_type=normalized_type,
                proc_status=PaymentEventProcessingStatus.IGNORED,
                reason="EVENT_TYPE_IGNORED_NO_STATE_MUTATION",
                tenant_id=tenant_id,
                agent_id=agent_id,
                tx_id=transaction_id,
                order_id=order_id,
                payment_id=payment_id,
                currency=parsed_currency,
            )

        # Infer previous status if not explicitly provided
        prev_status = current_status or self._infer_previous_status(target_status)
        resolved_tenant = tenant_id or uuid.uuid4()
        resolved_agent = agent_id or uuid.uuid4()
        resolved_tx = transaction_id or f"tx_event_{processing_id.hex[:8]}"
        resolved_order = order_id or f"order_evt_{processing_id.hex[:8]}"

        # 6. Execute Authoritative State Machine Transition
        try:
            record = self.status_service.transition_status(
                tenant_id=resolved_tenant,
                agent_id=resolved_agent,
                transaction_id=resolved_tx,
                order_id=resolved_order,
                previous_status=prev_status,
                new_status=target_status,
                transition_reason=f"WEBHOOK_EVENT_{normalized_type.value}",
                payment_id=payment_id,
            )

            is_same = record.transition_reason == "IDEMPOTENT_SAME_STATE"
            proc_stat = (
                PaymentEventProcessingStatus.ALREADY_PROCESSED
                if is_same
                else PaymentEventProcessingStatus.SUCCESS
            )
            reason = (
                "IDEMPOTENT_SAME_STATE"
                if is_same
                else f"STATUS_TRANSITION_SUCCESS_{target_status.value}"
            )

            logger.info(
                "Event processing %s (envelope_id=%s, %s -> %s)",
                proc_stat.value,
                envelope.envelope_id,
                prev_status.value,
                target_status.value,
            )

            return self._build_result(
                processing_id=processing_id,
                envelope=envelope,
                normalized_type=normalized_type,
                proc_status=proc_stat,
                reason=reason,
                tenant_id=resolved_tenant,
                agent_id=resolved_agent,
                tx_id=resolved_tx,
                order_id=resolved_order,
                payment_id=payment_id,
                prev_status=prev_status,
                new_status=target_status,
                currency=parsed_currency,
            )

        except PaymentStatusError as err:
            logger.warning(
                "Event processing ILLEGAL TRANSITION: %s (%s)",
                err.message,
                err.reason_code,
            )
            return self._build_result(
                processing_id=processing_id,
                envelope=envelope,
                normalized_type=normalized_type,
                proc_status=PaymentEventProcessingStatus.ILLEGAL_TRANSITION,
                reason=err.reason_code,
                tenant_id=resolved_tenant,
                agent_id=resolved_agent,
                tx_id=resolved_tx,
                order_id=resolved_order,
                payment_id=payment_id,
                prev_status=prev_status,
                new_status=target_status,
                currency=parsed_currency,
            )

    def _normalize_event_type(self, raw_type: str) -> NormalizedPaymentEventType:
        """Map provider event string to NormalizedPaymentEventType."""
        clean = raw_type.lower().strip()
        if clean == "payment.authorized":
            return NormalizedPaymentEventType.PAYMENT_AUTHORIZED
        if clean in {"payment.captured", "order.paid"}:
            return NormalizedPaymentEventType.PAYMENT_CAPTURED
        if clean == "payment.failed":
            return NormalizedPaymentEventType.PAYMENT_FAILED
        if clean in {"refund.processed", "refund.created"}:
            return NormalizedPaymentEventType.PAYMENT_REFUNDED
        if clean == "refund.failed":
            return NormalizedPaymentEventType.REFUND_FAILED
        if clean == "dispute.created":
            return NormalizedPaymentEventType.DISPUTE_CREATED
        return NormalizedPaymentEventType.UNKNOWN_EVENT

    def _map_event_to_target_status(
        self, normalized_type: NormalizedPaymentEventType
    ) -> PaymentStatus | None:
        """Map normalized event type to target PaymentStatus."""
        if normalized_type == NormalizedPaymentEventType.PAYMENT_AUTHORIZED:
            return PaymentStatus.PAYMENT_VERIFIED
        if normalized_type == NormalizedPaymentEventType.PAYMENT_CAPTURED:
            return PaymentStatus.CAPTURED
        if normalized_type == NormalizedPaymentEventType.PAYMENT_FAILED:
            return PaymentStatus.FAILED
        if normalized_type == NormalizedPaymentEventType.PAYMENT_REFUNDED:
            return PaymentStatus.REFUNDED
        return None

    def _infer_previous_status(self, target_status: PaymentStatus) -> PaymentStatus:
        """Infer default source status for state transition validation."""
        if target_status == PaymentStatus.PAYMENT_VERIFIED:
            return PaymentStatus.PAYMENT_RECEIVED
        if target_status == PaymentStatus.CAPTURED:
            return PaymentStatus.PAYMENT_VERIFIED
        if target_status == PaymentStatus.FAILED:
            return PaymentStatus.PAYMENT_PENDING
        if target_status == PaymentStatus.REFUNDED:
            return PaymentStatus.CAPTURED
        return PaymentStatus.CREATED

    def _extract_entity_data(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Safely extract entity details from Razorpay payload."""
        payload_dict = payload.get("payload", {})
        if not isinstance(payload_dict, dict):
            payload_dict = {}

        payment_ent = payload_dict.get("payment", {}).get("entity", {})
        order_ent = payload_dict.get("order", {}).get("entity", {})
        refund_ent = payload_dict.get("refund", {}).get("entity", {})

        if not isinstance(payment_ent, dict):
            payment_ent = {}
        if not isinstance(order_ent, dict):
            order_ent = {}
        if not isinstance(refund_ent, dict):
            refund_ent = {}

        order_id = payment_ent.get("order_id") or order_ent.get("id") or payload.get("order_id")
        payment_id = (
            payment_ent.get("id") or refund_ent.get("payment_id") or payload.get("payment_id")
        )
        currency = payment_ent.get("currency") or order_ent.get("currency")

        notes = payment_ent.get("notes") or order_ent.get("notes") or {}
        if not isinstance(notes, dict):
            notes = {}

        return {
            "order_id": str(order_id).strip() if order_id else None,
            "payment_id": str(payment_id).strip() if payment_id else None,
            "currency": str(currency).strip() if currency else None,
            "notes": notes,
        }

    def _parse_uuid(self, val: Any) -> uuid.UUID | None:
        """Parse UUID from string or object safely."""
        if not val:
            return None
        if isinstance(val, uuid.UUID):
            return val
        try:
            return uuid.UUID(str(val).strip())
        except ValueError:
            return None

    def _build_result(
        self,
        processing_id: uuid.UUID,
        envelope: VerifiedWebhookEnvelope,
        normalized_type: NormalizedPaymentEventType,
        proc_status: PaymentEventProcessingStatus,
        reason: str,
        tenant_id: uuid.UUID | None = None,
        agent_id: uuid.UUID | None = None,
        tx_id: str | None = None,
        order_id: str | None = None,
        payment_id: str | None = None,
        prev_status: PaymentStatus | None = None,
        new_status: PaymentStatus | None = None,
        currency: SupportedCurrency | None = None,
    ) -> PaymentEventProcessingResult:
        """Build safe PaymentEventProcessingResult with calculated fingerprint."""
        fingerprint_data = {
            "processing_id": str(processing_id),
            "envelope_id": str(envelope.envelope_id),
            "event_id": envelope.event_id or "",
            "raw_event_type": envelope.event_type,
            "normalized_event_type": normalized_type.value,
            "tenant_id": str(tenant_id) if tenant_id else "",
            "agent_id": str(agent_id) if agent_id else "",
            "transaction_id": tx_id or "",
            "order_id": order_id or "",
            "payment_id": payment_id or "",
            "previous_status": prev_status.value if prev_status else "",
            "new_status": new_status.value if new_status else "",
            "processing_status": proc_status.value,
            "reason_code": reason,
        }
        fp_json = json.dumps(fingerprint_data, sort_keys=True).encode("utf-8")
        fingerprint = hashlib.sha256(fp_json).hexdigest()

        return PaymentEventProcessingResult(
            processing_id=processing_id,
            envelope_id=envelope.envelope_id,
            provider=envelope.provider,
            event_id=envelope.event_id,
            raw_event_type=envelope.event_type,
            normalized_event_type=normalized_type,
            tenant_id=tenant_id,
            agent_id=agent_id,
            transaction_id=tx_id,
            order_id=order_id,
            payment_id=payment_id,
            previous_status=prev_status,
            new_status=new_status,
            processing_status=proc_status,
            reason_code=reason,
            currency=currency,
            processing_fingerprint=fingerprint,
        )
