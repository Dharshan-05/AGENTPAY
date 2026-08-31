"""ATIM PII Detector for identifying and redacting sensitive PII while preserving commercial intent."""

from __future__ import annotations

import logging
import re
from pydantic import BaseModel, Field

logger = logging.getLogger("agentpay.atim.security.pii_detector")

EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
UPI_PATTERN = re.compile(r"\b[a-zA-Z0-9.\-_]{2,64}@(upi|okicici|okhdfcbank|okaxis|ybl|paytm|barodampay)\b", re.IGNORECASE)
PAN_CARD_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")
SSN_PATTERN = re.compile(r"\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
BANK_ACCOUNT_PATTERN = re.compile(r"(?i)\b(account|acc|a/c)\s*[:#=]?\s*([0-9]{9,18})\b")


def luhn_check(card_str: str) -> bool:
    """Validate numeric string using Luhn algorithm."""
    digits = [int(c) for c in card_str if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


class PIIScanResult(BaseModel):
    """Structured PII detection report."""

    original_text: str
    sanitized_text: str
    pii_detected: bool = False
    pii_types: list[str] = Field(default_factory=list)
    redaction_count: int = 0


class ATIMPIIDetector:
    """Production service for PII scanning and commercial-safe redaction."""

    def scan_and_redact(self, text: str) -> PIIScanResult:
        """Scan input text for PII entities and apply deterministic redaction."""
        if not text:
            return PIIScanResult(
                original_text="",
                sanitized_text="",
                pii_detected=False,
            )

        sanitized = text
        pii_types: list[str] = []
        redaction_count = 0

        # 1. Credit Card Check with Luhn validation
        for match in CREDIT_CARD_PATTERN.finditer(text):
            candidate = match.group(0)
            if luhn_check(candidate):
                sanitized = sanitized.replace(candidate, "[REDACTED_CARD_NUMBER]")
                pii_types.append("CREDIT_CARD")
                redaction_count += 1

        # 2. Email Address Redaction
        if EMAIL_PATTERN.search(sanitized):
            matches = EMAIL_PATTERN.findall(sanitized)
            redaction_count += len(matches)
            pii_types.append("EMAIL")
            sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)

        # 3. UPI ID Redaction
        if UPI_PATTERN.search(sanitized):
            matches = UPI_PATTERN.findall(sanitized)
            redaction_count += len(matches)
            pii_types.append("UPI_ID")
            sanitized = UPI_PATTERN.sub("[REDACTED_UPI_ID]", sanitized)

        # 4. PAN Card / SSN Redaction
        if PAN_CARD_PATTERN.search(sanitized):
            matches = PAN_CARD_PATTERN.findall(sanitized)
            redaction_count += len(matches)
            pii_types.append("PAN_CARD")
            sanitized = PAN_CARD_PATTERN.sub("[REDACTED_GOVT_ID]", sanitized)

        if SSN_PATTERN.search(sanitized):
            matches = SSN_PATTERN.findall(sanitized)
            redaction_count += len(matches)
            pii_types.append("SSN")
            sanitized = SSN_PATTERN.sub("[REDACTED_SSN]", sanitized)

        # 5. Bank Account Number Redaction
        if BANK_ACCOUNT_PATTERN.search(sanitized):
            matches = BANK_ACCOUNT_PATTERN.findall(sanitized)
            redaction_count += len(matches)
            pii_types.append("BANK_ACCOUNT")
            sanitized = BANK_ACCOUNT_PATTERN.sub(r"\1=[REDACTED_ACCOUNT]", sanitized)

        pii_detected = len(pii_types) > 0
        if pii_detected:
            logger.info("ATIMPIIDetector redacted %d PII items of types: %s", redaction_count, pii_types)

        return PIIScanResult(
            original_text=text,
            sanitized_text=sanitized,
            pii_detected=pii_detected,
            pii_types=pii_types,
            redaction_count=redaction_count,
        )
