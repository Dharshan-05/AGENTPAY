"""Application layer exception hierarchy for AGENTPAY."""

from typing import Any

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class ApplicationError(AgentPayError):
    """Base exception for application use case and orchestration failures."""

    def __init__(
        self,
        message: str = "An application use case failure occurred.",
        code: ErrorCode | str = ErrorCode.APPLICATION_ERROR,
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize ApplicationError."""
        super().__init__(
            message=message,
            code=code,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class UseCaseError(ApplicationError):
    """Exception raised when an application use-case execution fails."""

    def __init__(
        self,
        message: str = "Use case execution failed.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize UseCaseError."""
        super().__init__(
            message=message,
            code=ErrorCode.APPLICATION_ERROR,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class ApplicationConflictError(ApplicationError):
    """Exception raised when a conflict prevents use-case execution."""

    def __init__(
        self,
        message: str = "Application operation conflict.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize ApplicationConflictError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class ReadinessError(ApplicationError):
    """Exception raised when application or downstream dependencies are not ready."""

    def __init__(
        self,
        message: str = "Service is not ready.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize ReadinessError."""
        super().__init__(
            message=message,
            code=ErrorCode.SERVICE_UNAVAILABLE,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )
