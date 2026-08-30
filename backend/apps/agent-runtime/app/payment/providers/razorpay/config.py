"""Razorpay Configuration & Secret Handling (Phase 286)."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr

logger = logging.getLogger("agentpay.payment.providers.razorpay.config")


class RazorpayConfiguration(BaseModel):
    """Safe Razorpay Integration Configuration (Phase 286)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    key_id: str | None = Field(default=None, description="Public Razorpay Key ID")
    key_secret: SecretStr | None = Field(default=None, description="Protected Razorpay Key Secret")
    webhook_secret: SecretStr | None = Field(
        default=None, description="Protected Razorpay Webhook Secret"
    )
    enabled: bool = Field(default=False, description="Razorpay integration enabled flag")
    environment_mode: str = Field(
        default="development", description="Execution mode (test, development, production)"
    )

    def validate_credentials(self) -> bool:
        """Validate presence and format of required configuration. Safe fail-closed logic."""
        if not self.enabled:
            logger.info("Razorpay integration is disabled.")
            return False

        if not self.key_id or not self.key_id.strip():
            logger.warning("Razorpay configuration invalid: key_id is missing.")
            return False

        if not self.key_secret or not self.key_secret.get_secret_value().strip():
            logger.warning("Razorpay configuration invalid: key_secret is missing.")
            return False

        return True

    @property
    def safe_summary(self) -> dict[str, Any]:
        """Return non-sensitive status summary REDACTING all secrets."""
        return {
            "enabled": self.enabled,
            "environment_mode": self.environment_mode,
            "key_id": self.key_id,
            "key_secret_configured": bool(
                self.key_secret and self.key_secret.get_secret_value().strip()
            ),
            "webhook_secret_configured": bool(
                self.webhook_secret and self.webhook_secret.get_secret_value().strip()
            ),
        }
