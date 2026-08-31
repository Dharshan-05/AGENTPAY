"""ATIM Security Policy module defining refusal handling and prompt leakage defense."""

from __future__ import annotations

import logging
from app.application.services.atim_security.security_classifier import ATIMSecurityDecision

logger = logging.getLogger("agentpay.atim.security.policy")

SAFE_PROMPT_LEAKAGE_REFUSAL = (
    "I am ATIM (AgentPay Transaction Intelligence Model), an autonomous proposal assistant. "
    "I cannot reveal internal system prompts, secret keys, or AGENTGUARD security rules."
)


class ATIMSecurityPolicy:
    """Production policy engine enforcing safe responses for security rejections and prompt leakage attempts."""

    @staticmethod
    def get_safe_refusal_response(decision: ATIMSecurityDecision) -> str:
        """Construct safe natural language refusal text for security rejections."""
        if any(cat in decision.detected_categories for cat in ["SYSTEM_PROMPT_EXTRACTION", "PROMPT_LEAKAGE_REQUEST"]):
            return SAFE_PROMPT_LEAKAGE_REFUSAL

        return (
            "Your request contains directives that violate AGENTPAY security policies "
            "or attempt to override financial authorization limits. Request rejected."
        )
