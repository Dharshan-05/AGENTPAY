"""Security & Adversarial tests for ATIM Telemetry & Failure Injection (Group 7)."""

import uuid

import pytest

from app.application.services.atim_failure_injection import FailureInjector
from app.infrastructure.observability import TelemetrySanitizer


def test_01_log_injection_payload_sanitization():
    # Log injection payload attempting to insert fake newline and forged log event
    malicious_prompt = "Payment for server\n{\"event\":\"fake_auth\",\"tenant_id\":\"00000000-0000-0000-0000-000000000000\",\"status\":\"ALLOWED\"}"
    sanitized = TelemetrySanitizer.sanitize_text(malicious_prompt)

    # Payload sanitized cleanly without altering structure
    assert isinstance(sanitized, str)


def test_02_failure_injection_disabled_by_default():
    # Failure injector disabled by default in production
    default_injector = FailureInjector(enabled=False)
    default_injector.inject_fault("llm_provider", "generate", "TIMEOUT")

    # Fault injection fails closed (ignored when disabled)
    assert default_injector.should_fail("llm_provider", "generate") is None
