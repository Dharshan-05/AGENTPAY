"""Infrastructure layer exception hierarchy for AGENTPAY."""

from typing import Any

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class InfrastructureError(AgentPayError):
    """Base exception for infrastructure adapter and persistence failures."""

    def __init__(
        self,
        message: str = "An infrastructure component failure occurred.",
        code: ErrorCode | str = ErrorCode.INFRASTRUCTURE_ERROR,
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize InfrastructureError."""
        super().__init__(
            message=message,
            code=code,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class DatabaseError(InfrastructureError):
    """Exception raised when a database operation fails."""

    def __init__(
        self,
        message: str = "Database operation failure.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize DatabaseError."""
        super().__init__(
            message=message,
            code=ErrorCode.INFRASTRUCTURE_ERROR,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class CacheError(InfrastructureError):
    """Exception raised when a cache operation fails."""

    def __init__(
        self,
        message: str = "Cache operation failure.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize CacheError."""
        super().__init__(
            message=message,
            code=ErrorCode.INFRASTRUCTURE_ERROR,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class ExternalServiceError(InfrastructureError):
    """Exception raised when an external API or service integration fails."""

    def __init__(
        self,
        message: str = "External service integration failure.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize ExternalServiceError."""
        super().__init__(
            message=message,
            code=ErrorCode.SERVICE_UNAVAILABLE,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )
