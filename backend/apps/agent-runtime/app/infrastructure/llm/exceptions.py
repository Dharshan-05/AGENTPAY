"""Exceptions for ATIM LLM Providers and Router."""

from __future__ import annotations


class LLMProviderError(Exception):
    """Base exception for LLM provider failures."""

    def __init__(self, message: str, provider: str | None = None, model: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.model = model


class LLMTimeoutError(LLMProviderError):
    """Raised when an LLM provider request times out."""


class LLMRateLimitError(LLMProviderError):
    """Raised when an LLM provider returns rate limit (HTTP 429)."""


class LLMAuthenticationError(LLMProviderError):
    """Raised when API key or authorization fails (HTTP 401/403)."""


class LLMValidationError(LLMProviderError):
    """Raised when LLM structured output fails Pydantic schema validation."""

    def __init__(
        self,
        message: str,
        raw_response: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        super().__init__(message, provider=provider, model=model)
        self.raw_response = raw_response
