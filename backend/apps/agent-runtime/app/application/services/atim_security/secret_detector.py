"""ATIM Secret Detector for credential scanning and deterministic redaction."""

from __future__ import annotations

import logging
import re
from pydantic import BaseModel, Field

logger = logging.getLogger("agentpay.atim.security.secret_detector")

# Regex patterns for credential & key detection
SECRET_PATTERNS = [
    ("OPENAI_KEY", re.compile(r"sk-proj-[a-zA-Z0-9_\-]{20,}")),
    ("ANTHROPIC_KEY", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{20,}")),
    ("GENERIC_SK_KEY", re.compile(r"\b(sk|pk)_(live|test)_[a-zA-Z0-9]{20,}\b")),
    ("BEARER_TOKEN", re.compile(r"(?i)bearer\s+[a-zA-Z0-9\-\._~\+\/]{15,}=*")),
    ("JWT_TOKEN", re.compile(r"eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}")),
    ("AWS_KEY", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("RAZORPAY_SECRET", re.compile(r"\brzp_(live|test)_[a-zA-Z0-9]{14,}\b")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH|PRIVATE) KEY-----[\s\S]*?-----END \1 KEY-----")),
    ("DATABASE_URL", re.compile(r"(?i)(postgres|postgresql|mongodb|redis):\/\/[^\s,]+")),
    (
        "KEY_VALUE_SECRET",
        re.compile(
            r"(?i)(password|passwd|secret|access_token|refresh_token|api_key|private_key|client_secret)[:=]\s*([^\s,]+)"
        ),
    ),
]


class SecretScanResult(BaseModel):
    """Structured report produced by ATIMSecretDetector."""

    original_text: str
    sanitized_text: str
    secrets_detected: bool = False
    secret_types: list[str] = Field(default_factory=list)
    redaction_count: int = 0


class ATIMSecretDetector:
    """Production service for secret credential scanning and deterministic redaction."""

    def scan_and_redact(self, text: str) -> SecretScanResult:
        """Scan input text for secrets and replace credential payloads with [REDACTED_SECRET]."""
        if not text:
            return SecretScanResult(
                original_text="",
                sanitized_text="",
                secrets_detected=False,
            )

        sanitized = text
        detected_types: list[str] = []
        redaction_count = 0

        for secret_label, pattern in SECRET_PATTERNS:
            if pattern.search(sanitized):
                matches = pattern.findall(sanitized)
                redaction_count += len(matches)
                detected_types.append(secret_label)
                if secret_label == "KEY_VALUE_SECRET":
                    sanitized = pattern.sub(r"\1=[REDACTED_SECRET]", sanitized)
                else:
                    sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)

        secrets_detected = len(detected_types) > 0
        if secrets_detected:
            logger.warning(
                "ATIMSecretDetector redacted %d credentials of types: %s",
                redaction_count,
                detected_types,
            )

        return SecretScanResult(
            original_text=text,
            sanitized_text=sanitized,
            secrets_detected=secrets_detected,
            secret_types=detected_types,
            redaction_count=redaction_count,
        )
