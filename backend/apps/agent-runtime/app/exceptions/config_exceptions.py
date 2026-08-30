"""Configuration exception module for AGENTPAY."""

from typing import Any

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class ConfigurationError(AgentPayError):
    """Exception raised when application configuration is invalid or missing."""

    def __init__(
        self,
        message: str = "Invalid application configuration.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize ConfigurationError."""
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_CONFIGURATION,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )
