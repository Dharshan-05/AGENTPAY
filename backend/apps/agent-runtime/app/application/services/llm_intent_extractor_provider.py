"""LLMIntentExtractorProvider for ATIM LLM intent extraction with fail-closed fallback."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from app.application.services.atim_constraint_engine import ATIMConstraintEngine
from app.application.services.intent_extraction_service import (
    BaseIntentExtractorProvider,
    RuleBasedIntentExtractorProvider,
)
from app.application.services.prompt_guard_service import PromptGuardService
from app.infrastructure.llm.prompts import ATIM_SYSTEM_PROMPT_V2
from app.infrastructure.llm.router import LLMRouter
from app.infrastructure.llm.schemas import LLMRequest
from app.schemas.agents import ExtractedEntities, StructuredIntent
from app.schemas.atim import ATIMProposedIntent
from app.application.services.atim_security import ATIMSecurityClassifier


logger = logging.getLogger("agentpay.atim.intent.extractor.provider")


class LLMIntentExtractorProvider(BaseIntentExtractorProvider):
    """Production LLM-backed Intent Extractor with automatic rule-engine fallback."""

    def __init__(
        self,
        router: LLMRouter | None = None,
        prompt_guard: PromptGuardService | None = None,
        security_classifier: ATIMSecurityClassifier | None = None,
        constraint_engine: ATIMConstraintEngine | None = None,
        fallback_provider: RuleBasedIntentExtractorProvider | None = None,
    ) -> None:
        self.router = router or LLMRouter()
        self.prompt_guard = prompt_guard or PromptGuardService()
        self.security_classifier = security_classifier or ATIMSecurityClassifier()
        self.constraint_engine = constraint_engine or ATIMConstraintEngine()
        self.fallback_provider = fallback_provider or RuleBasedIntentExtractorProvider()


    async def extract(
        self,
        request_text: str,
        context_metadata: dict[str, Any],
        target_model: str | None = None,
    ) -> StructuredIntent:
        """Extract structured intent using LLM provider with fallback to rule engine."""
        # 1. Sanitize user prompt & evaluate security decision via ATIMSecurityClassifier
        sec_decision = self.security_classifier.evaluate_security(request_text)
        if not sec_decision.allowed:
            logger.warning(
                "Security threat detected by ATIMSecurityClassifier (Severity: %s, Reasons: %s). Falling back to rule engine.",
                sec_decision.severity.value,
                sec_decision.reasons,
            )
            return await self.fallback_provider.extract(request_text, context_metadata)

        sanitization = self.prompt_guard.sanitize_prompt(request_text)

        # If prompt injection or high/critical security threat detected, block immediately
        if sanitization.contains_suspicious_injection or sanitization.risk_level in ("HIGH", "CRITICAL"):
            logger.warning(
                "Prompt injection threat detected by PromptGuard: %s.",
                sanitization.detected_threats,
            )
            return StructuredIntent(
                intent_id=uuid.uuid4(),
                action="prompt_injection",
                target="security_shield",
                entities=ExtractedEntities(amount=Decimal("0.00"), currency="USD"),
                parameters={"raw_prompt_length": len(request_text)},
                confidence=Decimal("1.00"),
            )

        # 2. Build LLMRequest
        corr_id = uuid.uuid4()

        llm_req = LLMRequest(
            prompt=sanitization.sanitized_prompt,
            system_prompt=ATIM_SYSTEM_PROMPT_V2,
            correlation_id=corr_id,
            temperature=0.0,
        )

        # 3. Attempt LLM Extraction via Router
        try:
            res = await self.router.generate_structured(
                schema=ATIMProposedIntent,
                request=llm_req,
                target_model=target_model,
            )
            raw_intent = res.data

            # 4. Normalize intent & constraints
            normalized_intent = self.constraint_engine.normalize_intent(raw_intent)

            # Map ATIMProposedIntent -> domain StructuredIntent
            entities = ExtractedEntities(
                amount=normalized_intent.amount,
                currency=normalized_intent.currency,
                merchant=normalized_intent.merchant,
                recipient=normalized_intent.recipient,
                target_id=normalized_intent.target,
                custom_entities={
                    "category": str(normalized_intent.category or ""),
                    "llm_provider": str(res.provider),
                    "llm_model": str(res.model),
                },
            )

            return StructuredIntent(
                intent_id=normalized_intent.intent_id,
                action=normalized_intent.action,
                target=normalized_intent.target,
                entities=entities,
                parameters={
                    "category": normalized_intent.category,
                    "correlation_id": str(res.correlation_id),
                },
                constraints={
                    c.name: c.value for c in normalized_intent.constraints
                },
                confidence=normalized_intent.confidence,
                source=f"atim_llm_{res.provider}",
            )


        except Exception as exc:
            logger.warning(
                "ATIM LLM intent extraction failed or unavailable: %s. Falling back to rule-based extractor.",
                exc,
            )
            return await self.fallback_provider.extract(request_text, context_metadata)
