"""Authentication domain exception abstractions."""

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class AuthenticationFailedError(AgentPayError):
    """Domain exception raised when user authentication fails."""

    def __init__(self, message: str = "Invalid credentials.") -> None:
        """Initialize AuthenticationFailedError with safe generic message."""
        super().__init__(
            message=message,
            code=ErrorCode.UNAUTHORIZED,
        )


class AccountLockedError(AgentPayError):
    """Domain exception raised when account is temporarily or permanently locked."""

    def __init__(
        self, message: str = "Account is temporarily locked. Please try again later."
    ) -> None:
        """Initialize AccountLockedError with safe lockout message."""
        super().__init__(
            message=message,
            code=ErrorCode.FORBIDDEN,
        )


class AccountDisabledError(AgentPayError):
    """Domain exception raised when account is disabled or suspended."""

    def __init__(self, message: str = "Account is disabled or suspended.") -> None:
        """Initialize AccountDisabledError with safe account state message."""
        super().__init__(
            message=message,
            code=ErrorCode.FORBIDDEN,
        )


class UserAlreadyExistsError(AgentPayError):
    """Domain exception raised when registering a user that already exists in tenant scope."""

    def __init__(self, message: str = "User with this email already exists within tenant.") -> None:
        """Initialize UserAlreadyExistsError with conflict message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class PermissionDeniedError(AgentPayError):
    """Domain exception raised when an authenticated principal lacks the required permission."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        permission: str | None = None,
    ) -> None:
        """Initialize PermissionDeniedError with safe public message."""
        details = {"required_permission": permission} if permission else None
        super().__init__(
            message=message,
            code=ErrorCode.FORBIDDEN,
            details=details,
        )


class ResourceNotFoundOrForbiddenError(AgentPayError):
    """Domain exception for IDOR-safe not-found-or-unauthorized resource responses."""

    def __init__(self, message: str = "Resource not found or access denied.") -> None:
        """Initialize ResourceNotFoundOrForbiddenError with safe 404 message."""
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )
