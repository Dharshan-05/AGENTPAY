"""Domain layer exception hierarchy for AGENTPAY."""

from typing import Any

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class DomainError(AgentPayError):
    """Base exception for all domain layer business logic failures."""

    def __init__(
        self,
        message: str = "A domain business logic rule failed.",
        code: ErrorCode | str = ErrorCode.DOMAIN_ERROR,
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize DomainError."""
        super().__init__(
            message=message,
            code=code,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class EntityNotFoundError(DomainError):
    """Exception raised when a requested domain entity is not found."""

    def __init__(
        self,
        message: str = "Requested entity was not found.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize EntityNotFoundError."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class BusinessRuleViolationError(DomainError):
    """Exception raised when a domain invariant or business rule is violated."""

    def __init__(
        self,
        message: str = "Domain business rule violation.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize BusinessRuleViolationError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )


class InvalidStateError(DomainError):
    """Exception raised when a domain entity is in an invalid state for an operation."""

    def __init__(
        self,
        message: str = "Invalid domain entity state.",
        details: dict[str, Any] | None = None,
        internal_message: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize InvalidStateError."""
        super().__init__(
            message=message,
            code=ErrorCode.DOMAIN_ERROR,
            details=details,
            internal_message=internal_message,
            cause=cause,
        )
