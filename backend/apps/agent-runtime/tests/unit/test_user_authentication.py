"""Unit tests for Phase 101 User Authentication foundation and password security."""

import pytest

from app.core.security import (
    PasswordPolicyError,
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.domain.exceptions.auth_exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AuthenticationFailedError,
    UserAlreadyExistsError,
)


def test_01_password_hashing_and_verification() -> None:
    """Verify password hashing produces bcrypt/pbkdf2 hash and timing-safe verification works."""
    raw_pass = "SecureP@ssw0rd2026!"
    hashed = hash_password(raw_pass)

    assert hashed != raw_pass
    assert hashed.startswith(("$2b$", "$pbkdf2-sha256$"))

    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(raw_pass, "") is False


def test_02_password_policy_validation() -> None:
    """Verify password strength policy enforces length and complexity criteria."""
    # Valid password
    validate_password_strength("ValidP@ssw0rd1!")

    # Too short
    with pytest.raises(PasswordPolicyError, match="at least 8 characters"):
        validate_password_strength("P@ss1")

    # Missing uppercase
    with pytest.raises(PasswordPolicyError, match="uppercase letter"):
        validate_password_strength("p@ssword1!")

    # Missing lowercase
    with pytest.raises(PasswordPolicyError, match="lowercase letter"):
        validate_password_strength("P@SSWORD1!")

    # Missing digit
    with pytest.raises(PasswordPolicyError, match="numerical digit"):
        validate_password_strength("P@ssword!")

    # Missing special character
    with pytest.raises(PasswordPolicyError, match="special character"):
        validate_password_strength("Password123")


def test_03_auth_exceptions_semantics() -> None:
    """Verify domain auth exception codes and safe default messages."""
    err_failed = AuthenticationFailedError()
    assert err_failed.code.value == "UNAUTHORIZED"
    assert err_failed.message == "Invalid credentials."

    err_locked = AccountLockedError()
    assert err_locked.code.value == "FORBIDDEN"
    assert "locked" in err_locked.message

    err_disabled = AccountDisabledError()
    assert err_disabled.code.value == "FORBIDDEN"
    assert "disabled" in err_disabled.message

    err_exists = UserAlreadyExistsError()
    assert err_exists.code.value == "RESOURCE_CONFLICT"
    assert "exists" in err_exists.message
