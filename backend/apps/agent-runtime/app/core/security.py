"""Security, password hashing, and credential validation infrastructure module."""

import re

from passlib.context import CryptContext

from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode

# Initialize Passlib CryptContext with bcrypt as default scheme and pbkdf2_sha256 as fallback
_pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)

# Password policy regex requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
UPPERCASE_PATTERN = re.compile(r"[A-Z]")
LOWERCASE_PATTERN = re.compile(r"[a-z]")
DIGIT_PATTERN = re.compile(r"\d")
SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]")


class PasswordPolicyError(AgentPayError):
    """Exception raised when a password fails policy criteria."""

    def __init__(self, message: str) -> None:
        """Initialize PasswordPolicyError with validation message."""
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
        )


def hash_password(password: str) -> str:
    """Hash plaintext password using modern salted cryptographic password hashing.

    Never logs, prints, or exposes the raw password string.
    """
    if not password:
        raise ValueError("Password string cannot be empty.")
    hashed: str = _pwd_context.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Timing-safe verification of plaintext password against stored hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        verified: bool = _pwd_context.verify(plain_password, hashed_password)
        return verified
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Evaluate whether a stored password hash requires rehashing due to scheme deprecation."""
    if not hashed_password:
        return False
    try:
        return bool(_pwd_context.needs_update(hashed_password))
    except Exception:
        return False


def validate_password_strength(password: str) -> None:
    """Validate plaintext password against security policy requirements.

    Enforces length boundaries, uppercase, lowercase, digit, and special character presence.
    Raises PasswordPolicyError on validation failure.
    """
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
        )
    if len(password) > PASSWORD_MAX_LENGTH:
        raise PasswordPolicyError(f"Password must not exceed {PASSWORD_MAX_LENGTH} characters.")
    if not UPPERCASE_PATTERN.search(password):
        raise PasswordPolicyError("Password must contain at least one uppercase letter.")
    if not LOWERCASE_PATTERN.search(password):
        raise PasswordPolicyError("Password must contain at least one lowercase letter.")
    if not DIGIT_PATTERN.search(password):
        raise PasswordPolicyError("Password must contain at least one numerical digit.")
    if not SPECIAL_CHAR_PATTERN.search(password):
        raise PasswordPolicyError("Password must contain at least one special character.")
