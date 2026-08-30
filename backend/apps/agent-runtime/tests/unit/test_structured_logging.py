"""Unit tests for Phase 017 Structured Logging JSON format, redaction, and serialization."""

import json
import logging

import pytest

from app.core.config import get_settings
from app.core.logging import JSONFormatter, configure_logging, sanitize_structured_data


def test_json_formatter_valid_json() -> None:
    """Verify JSONFormatter outputs valid, single-line parseable JSON."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="agentpay.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test event message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert isinstance(parsed, dict)
    assert parsed["message"] == "Test event message"


def test_json_formatter_required_base_fields() -> None:
    """Verify structured log events contain required base fields."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="agentpay.test",
        level=logging.WARNING,
        pathname="test.py",
        lineno=5,
        msg="Warning event",
        args=(),
        exc_info=None,
    )
    parsed = json.loads(formatter.format(record))

    assert "timestamp" in parsed
    assert parsed["timestamp"].endswith("Z")
    assert parsed["level"] == "WARNING"
    assert parsed["logger"] == "agentpay.test"
    assert parsed["message"] == "Warning event"


def test_json_formatter_service_identity_metadata() -> None:
    """Verify structured log events contain service metadata fields."""
    cfg = get_settings()
    formatter = JSONFormatter(cfg)
    record = logging.LogRecord(
        name="agentpay.service",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Service metadata check",
        args=(),
        exc_info=None,
    )
    parsed = json.loads(formatter.format(record))

    assert parsed["service"] == cfg.app_name
    assert parsed["environment"] == cfg.app_env.value
    assert parsed["version"] == cfg.app_version


def test_json_formatter_event_field() -> None:
    """Verify optional event field is serialized when provided in log record."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="agentpay.lifespan",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Application starting",
        args=(),
        exc_info=None,
    )
    record.event = "application.startup"
    parsed = json.loads(formatter.format(record))

    assert parsed.get("event") == "application.startup"


def test_json_formatter_extra_custom_fields() -> None:
    """Verify extra dictionary attributes are included in JSON log event payload."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="agentpay.extra",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Extra field test",
        args=(),
        exc_info=None,
    )
    record.component = "database_pool"
    record.retry_count = 3

    parsed = json.loads(formatter.format(record))
    assert parsed["component"] == "database_pool"
    assert parsed["retry_count"] == 3


def test_json_formatter_nested_secret_redaction() -> None:
    """Verify nested dictionaries with sensitive keys are recursively redacted."""
    data = {
        "user": "admin",
        "credentials": {
            "password": "SUPER_FAKE_SECRET_PASS",
            "api_key": "SUPER_FAKE_API_KEY_12345",
        },
        "tokens": ["normal_item", {"access_token": "SUPER_FAKE_JWT_TOKEN"}],
    }

    sanitized = sanitize_structured_data(data)
    assert sanitized["user"] == "admin"
    assert sanitized["credentials"]["password"] == "[REDACTED]"
    assert sanitized["credentials"]["api_key"] == "[REDACTED]"
    assert sanitized["tokens"][1]["access_token"] == "[REDACTED]"


def test_json_formatter_case_insensitive_redaction() -> None:
    """Verify case-insensitive sensitive key redaction."""
    data = {
        "PASSWORD": "secret_pass_1",
        "Api_Key": "secret_key_2",
        "Authorization": "Bearer secret_token_3",
    }

    sanitized = sanitize_structured_data(data)
    assert sanitized["PASSWORD"] == "[REDACTED]"
    assert sanitized["Api_Key"] == "[REDACTED]"
    assert sanitized["Authorization"] == "[REDACTED]"


def test_json_formatter_exception_serialization() -> None:
    """Verify exception information is serialized into structured dictionary."""
    formatter = JSONFormatter()
    try:
        raise ValueError("Synthetic test error for structured exception logging")
    except ValueError:
        import sys

        exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="agentpay.error",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="An error occurred",
            args=(),
            exc_info=exc_info,
        )

        parsed = json.loads(formatter.format(record))
        assert "exception" in parsed
        assert parsed["exception"]["type"] == "ValueError"
        assert "Synthetic test error" in parsed["exception"]["message"]
        assert "traceback" in parsed["exception"]


def test_json_formatter_non_serializable_fallback() -> None:
    """Verify non-JSON-serializable objects fall back gracefully using default=str."""

    class CustomUnserializableObject:
        def __str__(self) -> str:
            return "CustomObjectStringRepresentation"

    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="agentpay.fallback",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Fallback test",
        args=(),
        exc_info=None,
    )
    record.custom_obj = CustomUnserializableObject()

    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert parsed["custom_obj"] == "CustomObjectStringRepresentation"


def test_caplog_compatibility_with_json(caplog: pytest.LogCaptureFixture) -> None:
    """Verify caplog captures single-line JSON log messages."""
    configure_logging()
    logger = logging.getLogger("agentpay.structured")

    with caplog.at_level(logging.INFO):
        logger.info("Structured log test message")

    assert len(caplog.records) == 1
    assert "Structured log test message" in caplog.text
