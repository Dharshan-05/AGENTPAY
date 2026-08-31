"""ATIM Security Classifier for severity evaluation and fail-closed security decisions."""

from __future__ import annotations

import logging
from enum import StrEnum
from pydantic import BaseModel, Field

from app.application.services.atim_security.input_sanitizer import (
    ATIMInputSanitizer,
    SanitizedInputResult,
)

logger = logging.getLogger("agentpay.atim.security.classifier")


class SecuritySeverity(StrEnum):
    """Security risk severity classification levels."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ATIMSecurityDecision(BaseModel):
    """Security classification decision object."""

    allowed: bool = True
    execution_eligible: bool = True
    severity: SecuritySeverity = SecuritySeverity.NONE
    reasons: list[str] = Field(default_factory=list)
    sanitized_input: str = Field(default="")
    detected_categories: list[str] = Field(default_factory=list)


class ATIMSecurityClassifier:
    """Production Security Classifier enforcing fail-closed decision rules."""

    def __init__(self, sanitizer: ATIMInputSanitizer | None = None) -> None:
        self.sanitizer = sanitizer or ATIMInputSanitizer()

    def evaluate_security(self, raw_input: str) -> ATIMSecurityDecision:
        """Evaluate raw prompt input against security classifiers and produce a fail-closed decision."""
        if not raw_input:
            return ATIMSecurityDecision(
                allowed=True,
                execution_eligible=True,
                severity=SecuritySeverity.NONE,
                sanitized_input="",
            )

        sanitized_res: SanitizedInputResult = self.sanitizer.sanitize_input(raw_input)
        inj_res = sanitized_res.injection_result

        reasons: list[str] = []
        detected_cats = list(inj_res.categories)

        # Base severity from injection detector
        sev_str = inj_res.severity
        severity = SecuritySeverity[sev_str] if sev_str in SecuritySeverity.__members__ else SecuritySeverity.NONE

        if sanitized_res.contains_secret:
            reasons.append("SECRET_CREDENTIAL_DETECTED")
            if severity == SecuritySeverity.NONE:
                severity = SecuritySeverity.MEDIUM
            elif severity in (SecuritySeverity.HIGH, SecuritySeverity.MEDIUM):
                severity = SecuritySeverity.CRITICAL

        if sanitized_res.contains_pii:
            reasons.append("PII_ENTITIES_REDACTED")

        if inj_res.detected:
            reasons.extend(inj_res.matched_signals)

        # Determine authorization and execution eligibility
        allowed = True
        execution_eligible = True

        if severity in (SecuritySeverity.HIGH, SecuritySeverity.CRITICAL):
            allowed = False
            execution_eligible = False
            reasons.append(f"REJECTED_DUE_TO_{severity.value}_SECURITY_THREAT")
        elif severity == SecuritySeverity.MEDIUM:
            # Medium severity allows sanitized context but disables automatic financial execution eligibility
            execution_eligible = False
            reasons.append("FINANCIAL_EXECUTION_DISABLED_DUE_TO_MEDIUM_RISK")

        logger.info(
            "ATIMSecurityClassifier decision (Allowed: %s, ExecEligible: %s, Severity: %s, Reasons: %d)",
            allowed,
            execution_eligible,
            severity.value,
            len(reasons),
        )

        return ATIMSecurityDecision(
            allowed=allowed,
            execution_eligible=execution_eligible,
            severity=severity,
            reasons=reasons,
            sanitized_input=sanitized_res.sanitized_input,
            detected_categories=detected_cats,
        )
