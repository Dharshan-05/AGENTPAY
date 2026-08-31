"""Telemetry and log sanitization boundary module for ATIM (Phase 13 / Group 7)."""

import re
from typing import Any

SECRET_REDACTION_PATTERNS = [
    (re.compile(r"(?i)(bearer\s+[a-z0-9\-\._~\+\/]+=*)"), "[REDACTED_BEARER_TOKEN]"),
    (re.compile(r"(?i)(password|passwd|secret|api_key|private_key)[:=]\s*([^\s,]+)"), r"\1=[REDACTED_SECRET]"),
    (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), "[REDACTED_CARD_NUMBER]"),
    (re.compile(r"\b\d{3,4}\b"), "[REDACTED_CVV]"),
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[REDACTED_EMAIL]"),
]


class TelemetrySanitizer:
    """Sanitizer ensuring telemetry, logs, and trace attributes contain zero unredacted secrets or PII."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize raw string payload prior to logging or tracing."""
        if not text:
            return ""

        clean_text = text
        for pattern, replacement in SECRET_REDACTION_PATTERNS:
            clean_text = pattern.sub(replacement, clean_text)
        return clean_text

    @staticmethod
    def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
        """Recursively sanitize dictionary values."""
        sanitized: dict[str, Any] = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            if any(k in key_lower for k in ["password", "secret", "token", "api_key", "private_key"]):
                sanitized[key] = "[REDACTED_SECRET]"
            elif isinstance(value, str):
                sanitized[key] = TelemetrySanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = TelemetrySanitizer.sanitize_dict(value)
            else:
                sanitized[key] = value
        return sanitized
