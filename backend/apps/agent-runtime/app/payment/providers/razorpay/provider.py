"""Razorpay Integration PaymentProvider Implementation (Phase 286)."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.payment.providers.base import PaymentProvider
from app.payment.providers.razorpay.client import RazorpayClientFactory, RazorpayClientWrapper
from app.payment.providers.razorpay.config import RazorpayConfiguration

logger = logging.getLogger("agentpay.payment.providers.razorpay.provider")


class RazorpayProvider(PaymentProvider):
    """Production Razorpay Provider Integration (Phase 286).

    Establishes clean payment provider foundation without executing payments or creating orders.
    """

    def __init__(
        self,
        config: RazorpayConfiguration | None = None,
        client: RazorpayClientWrapper | None = None,
    ) -> None:
        if config is None:
            settings: Settings = get_settings()
            config = RazorpayConfiguration(
                key_id=settings.razorpay_key_id,
                key_secret=settings.razorpay_key_secret,
                webhook_secret=settings.razorpay_webhook_secret,
                enabled=settings.razorpay_enabled,
                environment_mode=settings.app_env.value,
            )

        self.config = config
        self._client = client or RazorpayClientFactory.create_client(self.config)

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "razorpay"

    @property
    def is_enabled(self) -> bool:
        """Check if Razorpay provider is enabled and configured."""
        if self._client and getattr(self._client, "is_mock", False):
            return True
        return self.config.enabled and self.config.validate_credentials()

    def validate_configuration(self) -> bool:
        """Validate configuration without exposing secrets."""
        return self.config.validate_credentials()

    def get_provider_status(self) -> dict[str, Any]:
        """Return safe non-sensitive diagnostic provider status map."""
        status = {
            "provider_name": self.provider_name,
            "enabled": self.is_enabled,
            "configuration": self.config.safe_summary,
            "client_initialized": self._client is not None,
        }
        if self._client:
            status["client_status"] = self._client.ping()
        return status

    def create_order(
        self,
        request: Any,
        auth_id: Any,
        auth_fp: str,
    ) -> Any:
        """Create a real Razorpay Order via RazorpayClientWrapper (Phase 289).

        Translates provider-neutral request into Razorpay API minor units payload,
        invokes the client wrapper, sanitizes the response, and returns PaymentOrderResult.
        Fails closed on uninitialized client or invalid response.
        """
        from app.schemas.payment import PaymentOrderResult, amount_to_minor_units

        if not self.is_enabled or self._client is None:
            raise RuntimeError(
                "Cannot create Razorpay order: "
                "Razorpay provider is not enabled or client is uninitialized."
            )

        amount_minor = amount_to_minor_units(request.amount, request.currency)

        # Receipt reference bounded to 40 chars max
        receipt = request.receipt or f"rcpt_{request.transaction_id}"
        if len(receipt) > 40:
            receipt = receipt[:40]

        # Sanitized safe notes
        notes = {
            "tenant_id": str(request.tenant_id),
            "agent_id": str(request.agent_id),
            "transaction_id": str(request.transaction_id),
            "idempotency_key": str(request.idempotency_key),
        }
        notes.update(request.notes or {})

        # Invoke client wrapper
        raw_res = self._client.create_order(
            amount_minor=amount_minor,
            currency=request.currency.value,
            receipt=receipt,
            notes=notes,
        )

        order_id = raw_res.get("id")
        if not order_id or not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("Razorpay API returned invalid or empty order ID. Failing closed.")

        status_str = raw_res.get("status", "created")

        return PaymentOrderResult(
            order_id=order_id.strip(),
            provider_name=self.provider_name,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            transaction_id=request.transaction_id,
            amount=request.amount,
            amount_minor_units=amount_minor,
            currency=request.currency,
            status=status_str,
            idempotency_key=request.idempotency_key,
            authorization_id=auth_id,
            authorization_fingerprint=auth_fp,
            payment_success=False,
            payment_verified=False,
            captured=False,
        )

    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
        tenant_id: Any = None,
    ) -> bool:
        """Verify payment cryptographic signature using server key secret (Phase 291)."""
        if not self.is_enabled or self._client is None:
            return False
        return self._client.verify_signature(order_id, payment_id, signature)

    def cancel_payment(
        self,
        order_id: str,
        payment_id: str | None = None,
        tenant_id: Any = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a payment / order via provider API (Phase 298)."""
        if not self.is_enabled or self._client is None:
            raise RuntimeError(
                "Cannot cancel Razorpay payment: Razorpay provider disabled or uninitialized."
            )
        notes = {"reason": reason} if reason else {}
        return self._client.cancel_order(order_id=order_id, notes=notes)

    def refund_payment(
        self,
        payment_id: str,
        amount_minor: int,
        currency: str,
        order_id: str | None = None,
        notes: dict[str, str] | None = None,
        tenant_id: Any = None,
    ) -> dict[str, Any]:
        """Refund a captured payment via provider API (Phase 299)."""
        if not self.is_enabled or self._client is None:
            raise RuntimeError(
                "Cannot refund Razorpay payment: Razorpay provider disabled or uninitialized."
            )
        return self._client.create_refund(
            payment_id=payment_id,
            amount_minor=amount_minor,
            currency=currency,
            notes=notes,
        )
