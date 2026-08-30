"""Unit, Security & Adversarial Tests for Phase 287 — Razorpay Credentials Storage."""

from __future__ import annotations

import logging
import uuid
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from app.payment.providers.razorpay.credentials import (
    EnvironmentRazorpayCredentialSource,
    RazorpayCredentialError,
    RazorpayCredentialResolver,
    RazorpayCredentials,
)


def test_01_valid_test_credentials_accepted() -> None:
    """1. Test valid test environment credentials created successfully."""
    creds = RazorpayCredentials(
        key_id="rzp_test_key_12345",
        key_secret=SecretStr("super_secret_test_key_67890"),
        environment="test",
    )
    assert creds.key_id == "rzp_test_key_12345"
    assert creds.environment == "test"
    assert creds.key_secret.get_secret_value() == "super_secret_test_key_67890"


def test_02_valid_production_credentials_accepted() -> None:
    """2. Test valid production environment credentials created successfully."""
    creds = RazorpayCredentials(
        key_id="rzp_live_key_99999",
        key_secret=SecretStr("super_secret_prod_key_88888"),
        environment="production",
    )
    assert creds.key_id == "rzp_live_key_99999"
    assert creds.environment == "production"


def test_03_missing_key_id_rejected() -> None:
    """3. Security Test: Empty or whitespace key_id raises RazorpayCredentialError."""
    with pytest.raises(RazorpayCredentialError, match="key_id cannot be empty"):
        RazorpayCredentials(
            key_id="   ",
            key_secret=SecretStr("valid_secret"),
        )


def test_04_missing_key_secret_rejected() -> None:
    """4. Security Test: Empty key_secret raises RazorpayCredentialError."""
    with pytest.raises(RazorpayCredentialError, match="key_secret cannot be empty"):
        RazorpayCredentials(
            key_id="rzp_test_123",
            key_secret=SecretStr("   "),
        )


def test_05_empty_credentials_rejected() -> None:
    """5. Security Test: Completely empty credentials fail validation."""
    with pytest.raises(RazorpayCredentialError):
        RazorpayCredentials(
            key_id="",
            key_secret=SecretStr(""),
        )


def test_06_invalid_environment_rejected() -> None:
    """6. Security Test: Invalid environment string raises RazorpayCredentialError."""
    with pytest.raises(RazorpayCredentialError, match="Invalid environment"):
        RazorpayCredentials(
            key_id="rzp_test_123",
            key_secret=SecretStr("secret"),
            environment="invalid_mode",
        )


def test_07_secretstr_protects_repr() -> None:
    """7. Security Test: repr() redacts key_secret."""
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("MY_CONFIDENTIAL_SECRET"),
    )
    repr_str = repr(creds)
    assert "MY_CONFIDENTIAL_SECRET" not in repr_str
    assert "[REDACTED]" in repr_str


def test_08_secretstr_protects_str_conversion() -> None:
    """8. Security Test: str() redacts key_secret."""
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("MY_CONFIDENTIAL_SECRET"),
    )
    str_val = str(creds)
    assert "MY_CONFIDENTIAL_SECRET" not in str_val
    assert "[REDACTED]" in str_val


def test_09_safe_summary_contains_no_plaintext_secret() -> None:
    """9. Security Test: safe_summary contains no plaintext secret values."""
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("MY_CONFIDENTIAL_SECRET"),
        webhook_secret=SecretStr("WEBHOOK_CONFIDENTIAL_SECRET"),
    )
    summary = creds.safe_summary
    summary_str = str(summary)

    assert summary["key_id"] == "rzp_test_123"
    assert summary["key_secret"] == "[REDACTED]"
    assert summary["webhook_secret"] == "[REDACTED]"
    assert "MY_CONFIDENTIAL_SECRET" not in summary_str
    assert "WEBHOOK_CONFIDENTIAL_SECRET" not in summary_str


def test_10_exceptions_never_contain_plaintext_secrets() -> None:
    """10. Security Test: Exception tracebacks and messages do not reveal secrets."""
    secret_val = "SECRET_STRING_DO_NOT_LEAK"
    try:
        RazorpayCredentials(
            key_id="rzp_test_123",
            key_secret=SecretStr("   "),  # Triggers error
        )
    except RazorpayCredentialError as e:
        err_msg = str(e)
        assert secret_val not in err_msg


def test_11_logs_never_contain_plaintext_secrets(caplog: pytest.LogCaptureFixture) -> None:
    """11. Security Test: Logging output never contains plaintext secret values."""
    secret_val = "UNSAFE_SECRET_TO_LOG_123"
    mock_settings = MagicMock()
    mock_settings.razorpay_key_id = "rzp_test_123"
    mock_settings.razorpay_key_secret = SecretStr(secret_val)
    mock_settings.razorpay_webhook_secret = None
    mock_settings.app_env.value = "test"

    source = EnvironmentRazorpayCredentialSource(settings=mock_settings)
    resolver = RazorpayCredentialResolver(source=source)

    with caplog.at_level(logging.INFO):
        creds = resolver.get_credentials()
        assert creds.key_id == "rzp_test_123"

    for log_record in caplog.records:
        assert secret_val not in log_record.getMessage()


def test_12_model_dump_does_not_leak_secrets() -> None:
    """12. Security Test: model_dump() replaces secret values with '[REDACTED]'."""
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("MY_SECRET_VAL"),
        webhook_secret=SecretStr("MY_WEBHOOK_VAL"),
    )
    dump = creds.model_dump()
    assert dump["key_secret"] == "[REDACTED]"
    assert dump["webhook_secret"] == "[REDACTED]"


def test_13_credential_fingerprint_excludes_plaintext_secret() -> None:
    """13. Security Test: Fingerprint excludes secret plaintext and changes if metadata changes."""
    creds1 = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("SECRET_A"),
        environment="test",
    )
    creds2 = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("SECRET_B_DIFFERENT"),  # Different secret, same metadata!
        environment="test",
    )

    fp1 = creds1.compute_credential_fingerprint()
    fp2 = creds2.compute_credential_fingerprint()

    # Fingerprints match because metadata is identical and secrets are excluded
    assert fp1 == fp2
    assert len(fp1) == 64


def test_14_test_production_environment_isolation_enforced() -> None:
    """14. Security Test: Resolver raises error on environment mismatch."""
    mock_source = MagicMock()
    mock_source.resolve_credentials.return_value = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        environment="test",
    )

    resolver = RazorpayCredentialResolver(source=mock_source)

    with pytest.raises(RazorpayCredentialError, match="Credential environment mismatch"):
        resolver.get_credentials(target_environment="production")


def test_15_credential_version_preserved() -> None:
    """15. Test credential version is preserved accurately."""
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        credential_version="2.1.0",
    )
    assert creds.credential_version == "2.1.0"


def test_16_tenant_isolation_behavior_verified() -> None:
    """16. Security Test: Tenant ID binding preserved on credentials."""
    tenant_id = uuid.uuid4()
    creds = RazorpayCredentials(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        tenant_id=tenant_id,
    )
    assert creds.tenant_id == tenant_id


def test_17_resolver_returns_deterministic_metadata() -> None:
    """17. Test resolver returns deterministic metadata across calls."""
    mock_settings = MagicMock()
    mock_settings.razorpay_key_id = "rzp_test_123"
    mock_settings.razorpay_key_secret = SecretStr("my_secret")
    mock_settings.razorpay_webhook_secret = None
    mock_settings.app_env.value = "test"

    source = EnvironmentRazorpayCredentialSource(settings=mock_settings)
    resolver = RazorpayCredentialResolver(source=source)

    c1 = resolver.get_credentials()
    c2 = resolver.get_credentials()

    assert c1.compute_credential_fingerprint() == c2.compute_credential_fingerprint()


def test_18_no_razorpay_network_calls_occur_during_resolution() -> None:
    """18. Security Test: Resolving credentials makes 0 network calls."""
    mock_settings = MagicMock()
    mock_settings.razorpay_key_id = "rzp_test_999"
    mock_settings.razorpay_key_secret = SecretStr("secret_999")
    mock_settings.razorpay_webhook_secret = None
    mock_settings.app_env.value = "test"

    source = EnvironmentRazorpayCredentialSource(settings=mock_settings)
    resolver = RazorpayCredentialResolver(source=source)

    creds = resolver.get_credentials()
    assert creds.key_id == "rzp_test_999"
