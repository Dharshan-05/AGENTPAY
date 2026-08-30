"""Unit tests for logging infrastructure, formatters, sanitization, and idempotency."""

import logging

import pytest

from app.core.config import get_settings
from app.core.logging import SecretSanitizingFilter, UTCFormatter, configure_logging


def test_configure_logging_idempotency() -> None:
    """Verify configure_logging is idempotent and prevents handler duplication."""
    configure_logging()
    root_logger = logging.getLogger()
    initial_handlers = [
        h for h in root_logger.handlers if not type(h).__module__.startswith("_pytest")
    ]

    # Re-run configure_logging multiple times
    configure_logging()
    configure_logging()

    current_handlers = [
        h for h in root_logger.handlers if not type(h).__module__.startswith("_pytest")
    ]

    assert len(current_handlers) == len(initial_handlers) == 1


def test_log_level_filtering(caplog: pytest.LogCaptureFixture) -> None:
    """Verify log level filtering suppresses DEBUG messages when level is INFO."""
    get_settings.cache_clear()
    configure_logging()

    logger = logging.getLogger("agentpay")
    with caplog.at_level(logging.INFO):
        logger.debug("Debug diagnostic message — should be suppressed")
        logger.info("Info operational message — should be captured")

    assert "Debug diagnostic message" not in caplog.text
    assert "Info operational message" in caplog.text


def test_utc_formatter() -> None:
    """Verify UTCFormatter produces ISO-8601 UTC timestamps ending with Z."""
    formatter = UTCFormatter("%(asctime)s | %(levelname)s | %(message)s")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)

    assert "Z | INFO | Test message" in formatted
    assert "T" in formatted


def test_secret_sanitizing_filter() -> None:
    """Verify SecretSanitizingFilter redacts sensitive password/token patterns."""
    log_filter = SecretSanitizingFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Connecting with password='super_secret_pass_123' and bearer='xyz'",
        args=(),
        exc_info=None,
    )

    log_filter.filter(record)
    assert "super_secret_pass_123" not in record.msg
    assert "[REDACTED]" in record.msg


def test_pytest_caplog_compatibility(caplog: pytest.LogCaptureFixture) -> None:
    """Verify pytest caplog fixture captures log messages emitted by agentpay loggers."""
    configure_logging()
    logger = logging.getLogger("agentpay.test")

    with caplog.at_level(logging.INFO):
        logger.info("Captured log event message")

    assert "Captured log event message" in caplog.text


def test_safe_summary_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify logging settings safe_summary contains zero unmasked secrets."""
    configure_logging()
    cfg = get_settings()
    logger = logging.getLogger("agentpay.config")

    with caplog.at_level(logging.INFO):
        logger.info("Active configuration: %s", cfg.safe_summary)

    assert "AGENTPAY API" in caplog.text
    assert "supersecret" not in caplog.text
