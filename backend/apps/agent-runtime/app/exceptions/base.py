"""Base application exception definition for AGENTPAY."""

from typing import Any

from app.core.logging import sanitize_structured_data
from app.exceptions.codes import ErrorCode


class AgentPayError(Exception):
    """Root base exception for all AGENTPAY application errors."""

    def __init__(
        self,
        message: str = "An internal error occurred.",
        code: ErrorCode | str = ErrorCode.INTERNAL_ERROR,
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize base AGENTPAY exception."""
        super().__init__(message)
        self.message = message
        self.code = code if isinstance(code, ErrorCode) else ErrorCode(str(code))
        self.details: dict[str, Any] | None = (
            sanitize_structured_data(details) if isinstance(details, dict) else None
        )
        self.internal_message = internal_message
        if cause:
            self.__cause__ = cause

    def __str__(self) -> str:
        """Return safe public error message representation."""
        return self.message

    def __repr__(self) -> str:
        """Return developer-facing exception string representation."""
        return f"{self.__class__.__name__}(code='{self.code.value}', message='{self.message}')"
