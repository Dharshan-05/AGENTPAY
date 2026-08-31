"""Unit tests for ATIMSecretDetector credential scanning and deterministic redaction."""

import pytest
from app.application.services.atim_security.secret_detector import ATIMSecretDetector


def test_01_redacts_openai_and_anthropic_keys():
    detector = ATIMSecretDetector()
    prompt = "sk-proj-abc1234567890abcdef12345678 and sk-ant-1234567890abcdef12345678"
    res = detector.scan_and_redact(prompt)

    assert res.secrets_detected is True
    assert "sk-proj-" not in res.sanitized_text
    assert "sk-ant-" not in res.sanitized_text
    assert "[REDACTED_SECRET]" in res.sanitized_text


def test_02_redacts_bearer_and_jwt_tokens():
    detector = ATIMSecretDetector()
    prompt = "Authorization: Bearer my_secret_bearer_token_1234567890"
    res = detector.scan_and_redact(prompt)

    assert res.secrets_detected is True
    assert "my_secret_bearer_token" not in res.sanitized_text


def test_03_redacts_razorpay_and_db_urls():
    detector = ATIMSecretDetector()
    prompt = "Connect to postgres://user:password@localhost:5432/db with rzp_live_secret123456789"
    res = detector.scan_and_redact(prompt)

    assert res.secrets_detected is True
    assert "postgres://" not in res.sanitized_text
    assert "rzp_live_" not in res.sanitized_text
