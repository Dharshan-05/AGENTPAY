"""Unit tests for Phase 107 Password Hashing, unique salts, verification, and repr safety."""

import uuid

import pytest

from app.core.security import hash_password, needs_rehash, verify_password
from app.infrastructure.database.models.user import User


def test_01_same_password_produces_different_hashes() -> None:
    """Verify password hashing generates unique cryptographic salts for identical inputs."""
    pwd = "SecureP@ssw0rd123!"
    hash1 = hash_password(pwd)
    hash2 = hash_password(pwd)

    assert hash1 != hash2
    assert hash1.startswith(("$2b$", "$pbkdf2"))
    assert hash2.startswith(("$2b$", "$pbkdf2"))


def test_02_valid_and_invalid_password_verification() -> None:
    """Verify verify_password succeeds for correct password and fails for incorrect password."""
    pwd = "SecureP@ssw0rd123!"
    pwd_hash = hash_password(pwd)

    assert verify_password(pwd, pwd_hash) is True
    assert verify_password("WrongP@ssw0rd!", pwd_hash) is False


def test_03_malformed_hash_and_empty_inputs() -> None:
    """Verify verify_password safely rejects empty inputs and malformed hash strings."""
    pwd = "SecureP@ssw0rd123!"
    valid_hash = hash_password(pwd)

    assert verify_password("", valid_hash) is False
    assert verify_password(pwd, "") is False
    assert verify_password(pwd, "invalid_malformed_hash_string") is False


def test_04_empty_password_hashing_rejection() -> None:
    """Verify hash_password raises ValueError when passed empty password string."""
    with pytest.raises(ValueError, match="cannot be empty"):
        hash_password("")


def test_05_needs_rehash_evaluation() -> None:
    """Verify needs_rehash evaluates whether hash scheme requires updating."""
    pwd = "SecureP@ssw0rd123!"
    valid_hash = hash_password(pwd)

    assert needs_rehash(valid_hash) is False
    assert needs_rehash("") is False


def test_06_user_repr_redacts_password_hash() -> None:
    """Verify User ORM model __repr__ redacts password_hash."""
    user = User(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        email="repr_test@example.com",
        password_hash="secret_bcrypt_hash_value",
        status="active",
    )
    repr_str = repr(user)

    assert "secret_bcrypt_hash_value" not in repr_str
    assert "password_hash" not in repr_str
    assert "repr_test@example.com" in repr_str
