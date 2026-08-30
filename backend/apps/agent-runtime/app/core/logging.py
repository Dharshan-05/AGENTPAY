"""Centralized logging infrastructure and structured JSON logging module for AGENTPAY."""

import json
import logging
import re
import sys
import traceback
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings, get_settings

# Sensitive pattern matching regex for secondary defensive redaction in raw text strings
SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"(?i)(password|secret|token|api_key|client_secret|authorization|bearer)\s*[:=]\s*['\"]?([^\s'\"]+)['\"]?"  # noqa: E501
    ),
    re.compile(r"SecretStr\(['\"].*?['\"]\)"),
]

# Sensitive dict keys for recursive case-insensitive structured redaction
SENSITIVE_KEYS: set[str] = {
    "password",
    "secret",
    "token",
    "api_key",
    "client_secret",
    "authorization",
    "bearer",
    "cookie",
    "private_key",
    "access_token",
    "refresh_token",
    "secret_key",
    "database_url",
    "redis_url",
    "jwt_secret",
}

# Standard logging fields to omit from extra payload parsing
LOGGING_BUILTIN_ATTRS: set[str] = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "event",
    "service",
    "environment",
    "version",
}


def sanitize_structured_data(data: Any) -> Any:
    """Recursively sanitize sensitive key/value pairs in nested data structures."""
    if isinstance(data, dict):
        sanitized_dict: dict[str, Any] = {}
        for key, value in data.items():
            key_str = str(key)
            key_lower = key_str.lower()
            if key_lower in SENSITIVE_KEYS or any(
                key_lower.endswith(f"_{s}") or key_lower.startswith(f"{s}_") for s in SENSITIVE_KEYS
            ):
                sanitized_dict[key_str] = "[REDACTED]"
            else:
                sanitized_dict[key_str] = sanitize_structured_data(value)
        return sanitized_dict
    elif isinstance(data, (list, tuple)):
        return [sanitize_structured_data(item) for item in data]
    elif isinstance(data, str):
        msg = data
        for pattern in SENSITIVE_PATTERNS:
            msg = (
                pattern.sub(r"\1=[REDACTED]", msg)
                if pattern.groups > 1
                else pattern.sub("[REDACTED]", msg)
            )
        return msg
    return data


class UTCFormatter(logging.Formatter):
    """Log formatter producing ISO-8601 UTC timestamps."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        """Format log record timestamp in UTC with trailing 'Z'."""
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class JSONFormatter(logging.Formatter):
    """Log formatter outputting structured, single-line JSON log events."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize JSONFormatter with application settings."""
        super().__init__()
        self.settings = settings or get_settings()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record into a single-line JSON string."""
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        timestamp_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Sanitize log record message
        message = record.getMessage()
        if isinstance(message, str):
            for pattern in SENSITIVE_PATTERNS:
                message = (
                    pattern.sub(r"\1=[REDACTED]", message)
                    if pattern.groups > 1
                    else pattern.sub("[REDACTED]", message)
                )

        log_event: dict[str, Any] = {
            "timestamp": timestamp_str,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "service": self.settings.app_name,
            "environment": self.settings.app_env.value,
            "version": self.settings.app_version,
        }

        # Optional event name field
        if hasattr(record, "event") and record.event:
            log_event["event"] = str(record.event)

        # Extract extra structured fields
        extra_fields: dict[str, Any] = {}
        for key, val in record.__dict__.items():
            if key not in LOGGING_BUILTIN_ATTRS and not key.startswith("_"):
                extra_fields[key] = val

        if extra_fields:
            sanitized_extra = sanitize_structured_data(extra_fields)
            if isinstance(sanitized_extra, dict):
                log_event.update(sanitized_extra)

        # Process exception information if present
        if record.exc_info:
            exc_type, exc_val, exc_tb = record.exc_info
            formatted_tb = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
            sanitized_tb = sanitize_structured_data(formatted_tb)
            log_event["exception"] = {
                "type": exc_type.__name__ if exc_type else "Exception",
                "message": sanitize_structured_data(str(exc_val)),
                "traceback": sanitized_tb,
            }

        return json.dumps(log_event, default=str)


class SecretSanitizingFilter(logging.Filter):
    """Logging filter providing secondary defensive redaction for sensitive patterns."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive keywords in log record messages."""
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in SENSITIVE_PATTERNS:
                msg = (
                    pattern.sub(r"\1=[REDACTED]", msg)
                    if pattern.groups > 1
                    else pattern.sub("[REDACTED]", msg)
                )
            record.msg = msg
        return True


_logging_configured: bool = False


def configure_logging(settings: Settings | None = None) -> None:
    """Configure centralized Python logging infrastructure with JSON structured output."""
    global _logging_configured
    active_settings = settings or get_settings()

    log_level = getattr(logging, active_settings.log_level.value.upper(), logging.INFO)

    root_logger = logging.getLogger()
    agentpay_logger = logging.getLogger("agentpay")
    app_logger = logging.getLogger("app")
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access = logging.getLogger("uvicorn.access")

    # Set log levels
    root_logger.setLevel(log_level)
    agentpay_logger.setLevel(log_level)
    app_logger.setLevel(log_level)
    uvicorn_logger.setLevel(log_level)
    uvicorn_access.setLevel(log_level)

    # Clear existing handlers to ensure idempotency (preserving test caplog handlers)
    for logger_obj in (root_logger, agentpay_logger, app_logger, uvicorn_logger, uvicorn_access):
        for h in list(logger_obj.handlers):
            if type(h).__module__.startswith("_pytest"):
                continue
            logger_obj.removeHandler(h)

    # Construct console handler targeting stdout with JSONFormatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    formatter = JSONFormatter(active_settings)
    handler.setFormatter(formatter)
    handler.addFilter(SecretSanitizingFilter())

    # Attach handler to root logger; child loggers propagate naturally
    root_logger.addHandler(handler)

    _logging_configured = True
