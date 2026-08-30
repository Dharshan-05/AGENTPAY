"""Payment Provider Abstract Base Interface (Phase 286)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PaymentProvider(ABC):
    """Abstract Base Class for Payment Provider Integrations (Phase 286).

    Prevents domain logic from directly depending on specific payment gateway SDKs.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return canonical provider name string (e.g. 'razorpay')."""
        ...

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Return True if provider configuration is valid and enabled."""
        ...

    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate required provider configuration. Must fail closed without exposing secrets."""
        ...

    @abstractmethod
    def get_provider_status(self) -> dict[str, Any]:
        """Return safe non-sensitive provider diagnostic status map."""
        ...

    @abstractmethod
    def create_order(
        self,
        request: Any,
        auth_id: Any,
        auth_fp: str,
    ) -> Any:
        """Create a payment order via provider API (Phase 289)."""
        ...

    @abstractmethod
    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
        tenant_id: Any = None,
    ) -> bool:
        """Verify payment cryptographic signature using server key secret (Phase 291)."""
        ...

    @abstractmethod
    def cancel_payment(
        self,
        order_id: str,
        payment_id: str | None = None,
        tenant_id: Any = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a payment / order via provider API (Phase 298)."""
        ...

    @abstractmethod
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
        ...
