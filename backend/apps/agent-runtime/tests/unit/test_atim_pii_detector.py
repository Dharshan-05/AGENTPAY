"""Unit tests for ATIMPIIDetector PII classification and commercial metadata preservation."""

import pytest
from app.application.services.atim_security.pii_detector import ATIMPIIDetector


def test_01_redacts_email_and_upi_ids():
    detector = ATIMPIIDetector()
    prompt = "Send receipt to john.doe@example.com or user@upi"
    res = detector.scan_and_redact(prompt)

    assert res.pii_detected is True
    assert "john.doe@example.com" not in res.sanitized_text
    assert "user@upi" not in res.sanitized_text
    assert "[REDACTED_EMAIL]" in res.sanitized_text
    assert "[REDACTED_UPI_ID]" in res.sanitized_text


def test_02_redacts_luhn_valid_credit_cards():
    detector = ATIMPIIDetector()
    prompt = "Card: 4532 0151 1283 0366"  # Luhn-valid Visa
    res = detector.scan_and_redact(prompt)

    assert res.pii_detected is True
    assert "4532" not in res.sanitized_text
    assert "[REDACTED_CARD_NUMBER]" in res.sanitized_text


def test_03_preserves_legitimate_commercial_metadata():
    detector = ATIMPIIDetector()
    prompt = "Order Apple iPhone 15 for 75000 INR from Amazon."
    res = detector.scan_and_redact(prompt)

    assert res.pii_detected is False
    assert res.sanitized_text == prompt
