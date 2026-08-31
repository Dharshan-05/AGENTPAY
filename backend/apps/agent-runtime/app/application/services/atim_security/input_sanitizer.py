"""ATIM Input Sanitizer orchestrator unifying secret, PII, and injection scanning."""

from __future__ import annotations

import logging
from pydantic import BaseModel, Field

from app.application.services.atim_security.injection_detector import (
    ATIMInjectionDetector,
    InjectionDetectionResult,
)
from app.application.services.atim_security.pii_detector import (
    ATIMPIIDetector,
    PIIScanResult,
)
from app.application.services.atim_security.secret_detector import (
    ATIMSecretDetector,
    SecretScanResult,
)

logger = logging.getLogger("agentpay.atim.security.input_sanitizer")


class SanitizedInputResult(BaseModel):
    """Unified sanitization result report."""

    original_input: str
    sanitized_input: str
    contains_secret: bool = False
    contains_pii: bool = False
    contains_injection: bool = False
    secret_result: SecretScanResult
    pii_result: PIIScanResult
    injection_result: InjectionDetectionResult


class ATIMInputSanitizer:
    """Production input sanitizer for multi-layered defense prior to LLM processing."""

    def __init__(
        self,
        secret_detector: ATIMSecretDetector | None = None,
        pii_detector: ATIMPIIDetector | None = None,
        injection_detector: ATIMInjectionDetector | None = None,
    ) -> None:
        self.secret_detector = secret_detector or ATIMSecretDetector()
        self.pii_detector = pii_detector or ATIMPIIDetector()
        self.injection_detector = injection_detector or ATIMInjectionDetector()

    def sanitize_input(self, raw_input: str) -> SanitizedInputResult:
        """Run input through secret redaction, PII scanning, and injection detection."""
        if not raw_input:
            empty_secret = SecretScanResult(original_text="", sanitized_text="")
            empty_pii = PIIScanResult(original_text="", sanitized_text="")
            empty_inj = InjectionDetectionResult(detected=False)
            return SanitizedInputResult(
                original_input="",
                sanitized_input="",
                secret_result=empty_secret,
                pii_result=empty_pii,
                injection_result=empty_inj,
            )

        # 1. Secret Redaction
        secret_res = self.secret_detector.scan_and_redact(raw_input)

        # 2. PII Redaction
        pii_res = self.pii_detector.scan_and_redact(secret_res.sanitized_text)

        # 3. Injection Detection
        inj_res = self.injection_detector.detect_injection(pii_res.sanitized_text)

        sanitized_final = pii_res.sanitized_text

        logger.info(
            "ATIMInputSanitizer complete (Creds: %s, PII: %s, Injection: %s)",
            secret_res.secrets_detected,
            pii_res.pii_detected,
            inj_res.detected,
        )



        return SanitizedInputResult(
            original_input=raw_input,
            sanitized_input=sanitized_final,
            contains_secret=secret_res.secrets_detected,
            contains_pii=pii_res.pii_detected,
            contains_injection=inj_res.detected,
            secret_result=secret_res,
            pii_result=pii_res,
            injection_result=inj_res,
        )
