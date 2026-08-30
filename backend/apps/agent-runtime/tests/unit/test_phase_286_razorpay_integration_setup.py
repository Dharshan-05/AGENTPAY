"""Unit & Security Tests for Phase 286 — Razorpay Integration Setup."""

from __future__ import annotations

from pydantic import SecretStr

from app.payment.providers.base import PaymentProvider
from app.payment.providers.razorpay.client import RazorpayClientFactory, RazorpayClientWrapper
from app.payment.providers.razorpay.config import RazorpayConfiguration
from app.payment.providers.razorpay.provider import RazorpayProvider


def test_01_razorpay_configuration_safe_summary_redacts_secrets() -> None:
    """1. Test RazorpayConfiguration safe_summary redacts secret values."""
    config = RazorpayConfiguration(
        key_id="rzp_test_12345",
        key_secret=SecretStr("super_secret_key_67890"),
        webhook_secret=SecretStr("webhook_secret_abcde"),
        enabled=True,
        environment_mode="test",
    )

    summary = config.safe_summary
    summary_str = str(summary)

    assert summary["key_id"] == "rzp_test_12345"
    assert summary["key_secret_configured"] is True
    assert summary["webhook_secret_configured"] is True
    assert "super_secret_key_67890" not in summary_str
    assert "webhook_secret_abcde" not in summary_str


def test_02_missing_credentials_fails_validation_safely() -> None:
    """2. Test missing key_id or key_secret causes validate_credentials to return False safely."""
    config_no_key = RazorpayConfiguration(
        key_id="",
        key_secret=SecretStr("secret"),
        enabled=True,
    )
    assert config_no_key.validate_credentials() is False

    config_no_secret = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr(""),
        enabled=True,
    )
    assert config_no_secret.validate_credentials() is False


def test_03_disabled_configuration_returns_not_enabled() -> None:
    """3. Test enabled=False causes validate_credentials and is_enabled to return False."""
    config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        enabled=False,
    )

    assert config.validate_credentials() is False
    provider = RazorpayProvider(config=config)
    assert provider.is_enabled is False


def test_04_provider_implements_payment_provider_interface() -> None:
    """4. Test RazorpayProvider extends PaymentProvider abstraction."""
    config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        enabled=True,
        environment_mode="test",
    )
    provider = RazorpayProvider(config=config)

    assert isinstance(provider, PaymentProvider)
    assert provider.provider_name == "razorpay"
    assert provider.is_enabled is True


def test_05_client_factory_creates_mockable_wrapper_in_test_env() -> None:
    """5. Test RazorpayClientFactory produces a mockable client boundary in test mode."""
    config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("secret"),
        enabled=True,
        environment_mode="test",
    )

    client = RazorpayClientFactory.create_client(config)
    assert client is not None
    assert isinstance(client, RazorpayClientWrapper)
    assert client.is_mock is True

    ping_res = client.ping()
    assert ping_res["status"] == "ready"
    assert ping_res["mock"] is True


def test_06_provider_status_returns_non_sensitive_summary() -> None:
    """6. Test get_provider_status returns non-sensitive summary without leaking secrets."""
    config = RazorpayConfiguration(
        key_id="rzp_test_123",
        key_secret=SecretStr("my_secret_val"),
        enabled=True,
        environment_mode="test",
    )
    provider = RazorpayProvider(config=config)
    status_data = provider.get_provider_status()

    assert status_data["provider_name"] == "razorpay"
    assert status_data["enabled"] is True
    assert status_data["client_initialized"] is True
    assert "my_secret_val" not in str(status_data)


def test_07_no_unsupported_legacy_methods_exist() -> None:
    """7. Security Test: No unsupported legacy capture or direct verification methods exist."""
    provider = RazorpayProvider()
    methods = dir(provider)

    assert "verify_payment" not in methods
    assert "process_webhook" not in methods
    assert "capture_payment" not in methods
