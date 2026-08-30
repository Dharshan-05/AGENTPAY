"""Unit tests for Phase 108 Password Policy Validation, edge cases, and Unicode support."""

import pytest

from app.core.security import PasswordPolicyError, validate_password_strength


def test_01_valid_password_passes_validation() -> None:
    """Verify valid passwords meeting all policy criteria pass validation."""
    valid_passwords = [
        "SecureP@ssw0rd123!",
        "Complex#Pass99$",
        "A1b2C3d4!@#$",
        "ÜnïcödëP@ssw0rd123!",
    ]
    for pwd in valid_passwords:
        validate_password_strength(pwd)  # Should not raise


def test_02_too_short_password_rejection() -> None:
    """Verify password under 8 characters raises PasswordPolicyError."""
    with pytest.raises(PasswordPolicyError, match="at least 8 characters"):
        validate_password_strength("P@ss1")


def test_03_too_long_password_rejection() -> None:
    """Verify password over 128 characters raises PasswordPolicyError."""
    long_pwd = "A1!" + "a" * 130
    with pytest.raises(PasswordPolicyError, match="not exceed 128 characters"):
        validate_password_strength(long_pwd)


def test_04_missing_uppercase_rejection() -> None:
    """Verify password missing uppercase character raises PasswordPolicyError."""
    with pytest.raises(PasswordPolicyError, match="uppercase letter"):
        validate_password_strength("securep@ssw0rd123!")


def test_05_missing_lowercase_rejection() -> None:
    """Verify password missing lowercase character raises PasswordPolicyError."""
    with pytest.raises(PasswordPolicyError, match="lowercase letter"):
        validate_password_strength("SECUREP@SSW0RD123!")


def test_06_missing_digit_rejection() -> None:
    """Verify password missing numerical digit raises PasswordPolicyError."""
    with pytest.raises(PasswordPolicyError, match="numerical digit"):
        validate_password_strength("SecureP@ssword!")


def test_07_missing_special_char_rejection() -> None:
    """Verify password missing special character raises PasswordPolicyError."""
    with pytest.raises(PasswordPolicyError, match="special character"):
        validate_password_strength("SecurePassword123")


def test_08_empty_input_rejection() -> None:
    """Verify empty password raises PasswordPolicyError."""
    with pytest.raises(PasswordPolicyError, match="at least 8 characters"):
        validate_password_strength("")
