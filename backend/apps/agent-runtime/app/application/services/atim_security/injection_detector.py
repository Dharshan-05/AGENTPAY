"""ATIM Injection Detector for prompt injection and adversarial threat defense."""

from __future__ import annotations

import base64
import logging
import re
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

logger = logging.getLogger("agentpay.atim.security.injection_detector")

# Injection Category Pattern Map
INJECTION_CATEGORY_PATTERNS = [
    (
        "DIRECT_INSTRUCTION_OVERRIDE",
        [
            re.compile(r"(?i)ignore\s+(all\s+)?(previous\s+)?(instructions|rules|system\s+prompts)"),
            re.compile(r"(?i)disregard\s+(all\s+)?(prior|previous)\s+(directives|rules|instructions)"),
            re.compile(r"(?i)forget\s+(all\s+)?(previous\s+)?(rules|instructions)"),
        ],
    ),
    (
        "ROLE_IMPERSONATION",
        [
            re.compile(r"(?i)you\s+are\s+now\s+(the\s+)?(payment\s+administrator|admin|system|root|supervisor)"),
            re.compile(r"(?i)act\s+as\s+(admin|administrator|system|security\s+engine|agentguard)"),
            re.compile(r"(?i)pretend\s+to\s+be\s+(a\s+)?(super_user|admin|payment_execution_engine)"),
        ],
    ),
    (
        "SYSTEM_PROMPT_EXTRACTION",
        [
            re.compile(r"(?i)(reveal|show|print|output|display)\s+(your\s+)?(system\s+prompt|hidden\s+instructions)"),
            re.compile(r"(?i)what\s+are\s+your\s+(initial|system|hidden)\s+(instructions|directives|rules)"),
            re.compile(r"(?i)dump\s+(system\s+prompt|developer\s+instructions)"),
        ],
    ),
    (
        "SECURITY_BYPASS",
        [
            re.compile(r"(?i)bypass\s+(agentguard|fraudguard|security\s+rules|risk\s+check)"),
            re.compile(r"(?i)skip\s+(fraud\s+checks|hitl\s+approval|spending\s+limit\s+check)"),
            re.compile(r"(?i)disable\s+(security|fraudguard|agentguard|policy\s+engine)"),
        ],
    ),
    (
        "POLICY_OVERRIDE",
        [
            re.compile(r"(?i)increase\s+(my\s+)?(spending\s+limit|budget)"),
            re.compile(r"(?i)grant\s+(unlimited\s+budget|infinite\s+limit|unlimited\s+spending)"),
            re.compile(r"(?i)(override|ignore)\s+(policy\s+limits|spending\s+rules|policy\s+rules)"),
            re.compile(r"(?i)unlimited\s+spending"),
        ],
    ),

    (
        "TOOL_AUTHORIZATION_MANIPULATION",
        [
            re.compile(r"(?i)authorize\s+payment\s+directly"),
            re.compile(r"(?i)call\s+payment\.authorize"),
            re.compile(r"(?i)execute\s+payment\s+without\s+approval"),
        ],
    ),
    (
        "DELIMITER_ATTACK",
        [
            re.compile(r"</untrusted_[a-zA-Z_]+>"),
            re.compile(r"<system>|<admin>|<developer>"),
            re.compile(r"```(system|developer|admin|agentguard)"),
            re.compile(r"(?i)begin\s+system\s+message"),
            re.compile(r"(?i)system\s+directive:"),
        ],
    ),
    (
        "PROMPT_LEAKAGE_REQUEST",
        [
            re.compile(r"(?i)show\s+agentguard\s+rules"),
            re.compile(r"(?i)tell\n?\s*me\s+(the\s+)?secret\s+api\s+key"),
            re.compile(r"(?i)output\s+(all\s+)?internal\s+prompts"),
        ],
    ),
    (
        "INDIRECT_INJECTION",
        [
            re.compile(r"(?i)system:\s*ignore\s+fraud\s+checks"),
            re.compile(r"(?i)note\s+to\s+ai:\s*approve\s+this\s+transaction"),
            re.compile(r"(?i)instruction:\s*override\s+budget"),
        ],
    ),
]

# Zero-width / obfuscation characters
ZERO_WIDTH_CHARS = re.compile(r"[\u200B-\u200D\uFEFF]")


class InjectionDetectionResult(BaseModel):
    """Structured report returned by ATIMInjectionDetector."""

    detected: bool
    severity: Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"] = "NONE"
    categories: list[str] = Field(default_factory=list)
    matched_signals: list[str] = Field(default_factory=list)
    confidence: Decimal = Decimal("0.00")
    action: Literal["ALLOW", "SANITIZE", "REJECT"] = "ALLOW"


class ATIMInjectionDetector:
    """Production injection detection engine combining pattern scanning, delimiter checks, and decoding analysis."""

    def detect_injection(self, text: str) -> InjectionDetectionResult:
        """Scan input text for direct, indirect, delimiter, and encoded injection attacks."""
        if not text:
            return InjectionDetectionResult(
                detected=False,
                severity="NONE",
                confidence=Decimal("0.00"),
                action="ALLOW",
            )

        categories: list[str] = []
        matched_signals: list[str] = []

        # 1. Zero-width character & obfuscation scan
        clean_text = ZERO_WIDTH_CHARS.sub("", text)
        if len(clean_text) < len(text):
            categories.append("ENCODED_INJECTION")
            matched_signals.append("ZERO_WIDTH_CHARACTERS_DETECTED")

        # 2. Base64 payload decoding analysis
        try:
            b64_matches = re.findall(r"\b[A-Za-z0-9+/]{20,}={0,2}\b", clean_text)
            for b64_candidate in b64_matches:
                decoded = base64.b64decode(b64_candidate, validate=True).decode("utf-8", errors="ignore")
                if any(kw in decoded.lower() for kw in ["ignore instructions", "override", "bypass", "system"]):
                    categories.append("ENCODED_INJECTION")
                    matched_signals.append(f"BASE64_INJECTION_PAYLOAD: '{b64_candidate[:15]}...'")
        except Exception:
            pass

        # 3. Category pattern matching
        for category_name, patterns in INJECTION_CATEGORY_PATTERNS:
            for pattern in patterns:
                match = pattern.search(clean_text)
                if match:
                    if category_name not in categories:
                        categories.append(category_name)
                    matched_signals.append(f"{category_name}: '{match.group(0)}'")

        detected = len(categories) > 0

        # 4. Severity & Action Determination
        if not detected:
            severity = "NONE"
            action = "ALLOW"
            confidence = Decimal("0.00")
        else:
            critical_categories = {
                "SECURITY_BYPASS",
                "POLICY_OVERRIDE",
                "TOOL_AUTHORIZATION_MANIPULATION",
                "DELIMITER_ATTACK",
            }
            high_categories = {
                "DIRECT_INSTRUCTION_OVERRIDE",
                "ROLE_IMPERSONATION",
                "SYSTEM_PROMPT_EXTRACTION",
                "PROMPT_LEAKAGE_REQUEST",
                "INDIRECT_INJECTION",
                "ENCODED_INJECTION",
            }

            if any(cat in critical_categories for cat in categories):
                severity = "CRITICAL"
                action = "REJECT"
                confidence = Decimal("0.99")
            elif any(cat in high_categories for cat in categories):
                severity = "HIGH"
                action = "REJECT"
                confidence = Decimal("0.90")
            elif len(categories) > 1:
                severity = "MEDIUM"
                action = "REJECT"
                confidence = Decimal("0.75")
            else:
                severity = "LOW"
                action = "SANITIZE"
                confidence = Decimal("0.50")

        if detected:
            logger.warning(
                "ATIMInjectionDetector identified threats (Severity: %s, Action: %s, Categories: %s)",
                severity,
                action,
                categories,
            )

        return InjectionDetectionResult(
            detected=detected,
            severity=severity,
            categories=categories,
            matched_signals=matched_signals,
            confidence=confidence,
            action=action,
        )
