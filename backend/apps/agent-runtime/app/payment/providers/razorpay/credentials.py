"""Razorpay Credential Management & Secret Protection Boundary (Phase 287)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.core.config import Settings, get_settings

logger = logging.getLogger("agentpay.payment.providers.razorpay.credentials")


class RazorpayCredentialError(Exception):
    """Domain exception for Razorpay credential errors. Must never reveal secrets."""


class RazorpayCredentials(BaseModel):
    """Immutable, typed Razorpay Credential model with secret protection (Phase 287)."""

    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    key_id: str = Field(..., description="Public Razorpay Key ID")
    key_secret: SecretStr = Field(..., description="Protected Razorpay Key Secret")
    webhook_secret: SecretStr | None = Field(
        default=None, description="Protected Razorpay Webhook Secret"
    )
    merchant_id: str | None = Field(default=None, description="Optional merchant identifier")
    environment: str = Field(
        default="test", description="Execution mode (test, development, staging, production)"
    )
    credential_version: str = Field(
        default="1.0.0", description="Credential schema/rotation version"
    )
    activated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Credential activation timestamp UTC"
    )
    expires_at: datetime | None = Field(
        default=None, description="Optional credential expiration timestamp UTC"
    )
    tenant_id: uuid.UUID | None = Field(
        default=None, description="Optional tenant UUID binding for multi-tenant isolation"
    )

    @field_validator("key_id")
    @classmethod
    def validate_key_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise RazorpayCredentialError("Razorpay key_id cannot be empty.")
        return v.strip()

    @field_validator("key_secret")
    @classmethod
    def validate_key_secret(cls, v: SecretStr) -> SecretStr:
        if not v or not v.get_secret_value().strip():
            raise RazorpayCredentialError("Razorpay key_secret cannot be empty.")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"test", "development", "staging", "production", "local"}
        clean = v.lower().strip()
        if clean not in allowed:
            raise RazorpayCredentialError(
                f"Invalid environment '{v}'. Allowed environments: {sorted(allowed)}"
            )
        return clean

    def __repr__(self) -> str:
        """Protect repr from revealing secrets."""
        return (
            f"RazorpayCredentials(key_id='{self.key_id}', key_secret='[REDACTED]', "
            f"environment='{self.environment}', version='{self.credential_version}')"
        )

    def __str__(self) -> str:
        """Protect str conversion from revealing secrets."""
        return self.__repr__()

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to guarantee secrets are redacted in output dictionary."""
        d = super().model_dump(*args, **kwargs)
        if "key_secret" in d:
            d["key_secret"] = "[REDACTED]"
        if "webhook_secret" in d and d["webhook_secret"] is not None:
            d["webhook_secret"] = "[REDACTED]"
        return d

    @property
    def safe_summary(self) -> dict[str, Any]:
        """Return non-sensitive status summary REDACTING all secret values."""
        return {
            "provider": "razorpay",
            "key_id": self.key_id,
            "key_secret": "[REDACTED]",
            "webhook_secret": "[REDACTED]" if self.webhook_secret else None,
            "environment": self.environment,
            "credential_version": self.credential_version,
            "merchant_id": self.merchant_id,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    def compute_credential_fingerprint(self) -> str:
        """Compute SHA-256 fingerprint excluding plaintext secret values."""
        payload = {
            "provider": "razorpay",
            "key_id": self.key_id,
            "environment": self.environment,
            "credential_version": self.credential_version,
            "merchant_id": self.merchant_id or "",
            "tenant_id": str(self.tenant_id) if self.tenant_id else "",
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class RazorpayCredentialSource(ABC):
    """Abstract Credential Source interface for resolving Razorpay credentials (Phase 287)."""

    @abstractmethod
    def resolve_credentials(
        self,
        tenant_id: uuid.UUID | None = None,
        environment: str | None = None,
    ) -> RazorpayCredentials:
        """Resolve RazorpayCredentials for the given tenant and environment."""
        ...


class EnvironmentRazorpayCredentialSource(RazorpayCredentialSource):
    """Configuration/Environment-backed Razorpay Credential Source (Phase 287)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def resolve_credentials(
        self,
        tenant_id: uuid.UUID | None = None,
        environment: str | None = None,
    ) -> RazorpayCredentials:
        env_mode = (environment or self.settings.app_env.value).lower().strip()

        key_id = self.settings.razorpay_key_id
        key_secret = self.settings.razorpay_key_secret
        webhook_secret = self.settings.razorpay_webhook_secret

        if not key_id or not key_id.strip():
            raise RazorpayCredentialError(
                "Razorpay credentials not configured: RAZORPAY_KEY_ID is missing."
            )

        if not key_secret or not key_secret.get_secret_value().strip():
            raise RazorpayCredentialError(
                "Razorpay credentials not configured: RAZORPAY_KEY_SECRET is missing."
            )

        return RazorpayCredentials(
            key_id=key_id,
            key_secret=key_secret,
            webhook_secret=webhook_secret,
            environment=env_mode,
            tenant_id=tenant_id,
        )


class RazorpayCredentialResolver:
    """Service resolving and validating RazorpayCredentials safely (Phase 287)."""

    def __init__(self, source: RazorpayCredentialSource | None = None) -> None:
        self.source = source or EnvironmentRazorpayCredentialSource()

    def get_credentials(
        self,
        tenant_id: uuid.UUID | None = None,
        target_environment: str | None = None,
    ) -> RazorpayCredentials:
        """Resolve, validate, and return RazorpayCredentials safely (Phase 287)."""
        logger.info(
            "Resolving Razorpay credentials (tenant_id=%s, target_env=%s)",
            tenant_id,
            target_environment,
        )
        creds = self.source.resolve_credentials(tenant_id=tenant_id, environment=target_environment)

        # Environment isolation check: prevent test/production mixing
        if target_environment and creds.environment != target_environment.lower().strip():
            raise RazorpayCredentialError(
                f"Credential environment mismatch! Target '{target_environment}' "
                f"!= Resolved '{creds.environment}'"
            )

        return creds
