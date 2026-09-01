"""Intent Extraction application service for AGENTPAY (Phase 140).

Responsibilities:
    - Extract candidate semantic intent and structured entities from input request text
    - Pluggable provider abstraction (`BaseIntentExtractorProvider`) with rule/regex baseline
    - Ensure zero secret leakage (sanitizes passwords, keys, bearer tokens)
    - Enforce financial precision using `Decimal` and explicit currency codes
    - REPRESENTATIONAL ONLY: MUST NOT execute payments, call tools, create plans, or mutate state
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import abc
import logging
import re
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError, IntentExtractionError
from app.infrastructure.database.models.agent import Agent
from app.schemas.agents import (
    ExtractedEntities,
    IntentExtractionResponse,
    StructuredIntent,
)

logger = logging.getLogger("agentpay.agent.intent_extraction.service")

# Regex pattern for basic secret redaction in extracted text
SECRET_PATTERN = re.compile(
    r"(?i)(password|secret|bearer\s+[a-z0-9\-\._~\+\/]+=*|api_key|token)[:=]\s*([^\s,]+)"
)


class BaseIntentExtractorProvider(abc.ABC):
    """Abstract interface for Intent Extractor Providers (Rule-based or LLM-backed)."""

    @abc.abstractmethod
    async def extract(
        self, request_text: str, context_metadata: dict[str, Any]
    ) -> StructuredIntent:
        """Extract structured intent from request text."""
        ...


class RuleBasedIntentExtractorProvider(BaseIntentExtractorProvider):
    """Deterministic, production-grade rule/regex intent extractor baseline provider."""

    async def extract(
        self, request_text: str, context_metadata: dict[str, Any]
    ) -> StructuredIntent:
        """Extract structured intent using deterministic pattern matching."""
        sanitized_text = SECRET_PATTERN.sub(r"\1=[REDACTED]", request_text)
        lower_text = sanitized_text.lower()

        # Extract Monetary Amount & Currency
        amount: Decimal | None = None
        currency: str | None = None

        # Matches ₹500, $100.50, 500 USD, 100 EUR, 50.25 INR
        curr_match = re.search(
            r"(?:([₹\$€\$])\s*([0-9]+(?:\.[0-9]{1,2})?))|(?:([0-9]+(?:\.[0-9]{1,2})?)\s*(usd|inr|eur|gbp))",  # noqa: E501
            lower_text,
        )
        if curr_match:
            symbol, amt1, amt2, curr_code = curr_match.groups()
            raw_amt = amt1 or amt2
            if raw_amt:
                try:
                    amount = Decimal(raw_amt)
                except InvalidOperation:
                    amount = None

            if symbol == "₹" or (curr_code and curr_code == "inr"):
                currency = "INR"
            elif symbol == "$" or (curr_code and curr_code == "usd"):
                currency = "USD"
            elif symbol == "€" or (curr_code and curr_code == "eur"):
                currency = "EUR"
            elif curr_code:
                currency = curr_code.upper()

        # Extract Merchant
        merchant: str | None = None
        m_match = re.search(r"(?:to|at|from)\s+merchant\s+([a-z0-9_\-]+)", lower_text)
        if not m_match:
            m_match = re.search(r"merchant\s+([a-z0-9_\-]+)", lower_text)
        if m_match:
            merchant = m_match.group(1).strip()

        # Infer Action
        clean_prompt = lower_text.strip()
        greetings = {
            "hi", "hello", "hey", "hi there", "good morning", "good afternoon",
            "good evening", "how are you", "thank you", "thanks", "ok", "okay",
            "test", "ping"
        }
        queries = {
            "what can you do?", "what can you do", "help", "who are you"
        }

        # 0. Check Prompt Injection Security Attack Phrases
        from app.application.services.prompt_guard_service import SUSPICIOUS_INJECTION_PATTERNS
        if any(pat.search(clean_prompt) for pat in SUSPICIOUS_INJECTION_PATTERNS):
            return StructuredIntent(
                intent_id=uuid.uuid4(),
                action="prompt_injection",
                target="security_shield",
                entities=ExtractedEntities(amount=Decimal("0.00"), currency="USD"),
                parameters={"raw_prompt_length": len(sanitized_text)},
                constraints=context_metadata.get("constraints", {}),
                confidence=Decimal("1.00"),
            )

        # Greetings & General Queries (Checked before general keyword matches)
        if clean_prompt in greetings or any(clean_prompt.startswith(g + " ") for g in ["hi", "hello", "hey", "good morning"]):
            action = "greeting"
            target = None
            confidence = Decimal("1.00")
        elif clean_prompt in queries or any(q in clean_prompt for q in queries):
            action = "general_query"
            target = None
            confidence = Decimal("1.00")
        elif any(w in lower_text for w in ["which seller", "safest seller", "seller is safest", "seller trust", "seller rating"]):
            action = "seller_analysis"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["genuine", "is this product genuine", "product risky", "is product 1 risky", "counterfeit", "product risk"]):
            action = "product_risk_analysis"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["price is real", "check this price", "check this product price", "price analysis", "price anomaly"]):
            action = "price_analysis"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["compare", "comparison", "difference between"]):
            action = "product_comparison"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["tell me about", "specs of", "details of"]):
            action = "product_details"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(lower_text.startswith(w) or f" {w} " in f" {lower_text} " for w in ["buy", "purchase"]):
            action = "purchase_request"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["show my transactions", "check my last payment", "transaction history", "lookup payment"]):
            action = "transaction_query"
            target = "ledger"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in [
            "laptop", "phone", "mobile", "smartphone", "smartwatch", "headphones", "earbuds", "tablet", "tv", "monitor", "keyboard", "camera", "gaming", "coding", "under", "undr", "below", "budget", "price", "seller", "deal", "cheapest"
        ]):
            if any(w in lower_text for w in ["recommend", "suggest", "best for", "which mobile is best", "which phone is best"]):
                action = "product_recommendation"
            else:
                action = "product_search"
            target = "commerce"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["pay", "payment", "send money", "transfer", "authorize"]):
            action = "payment"
            target = "merchant" if merchant else "recipient"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["refund", "reimburse"]):
            action = "refund"
            target = "transaction"
            confidence = Decimal("0.90")
        elif any(w in lower_text for w in ["balance", "funds"]):
            action = "balance_query"
            target = "wallet"
            confidence = Decimal("0.95")
        elif any(w in lower_text for w in ["transaction", "history", "lookup"]):
            action = "transaction_lookup"
            target = "ledger"
            confidence = Decimal("0.90")
        elif any(w in lower_text for w in ["merchant"]):
            action = "merchant_lookup"
            target = "merchant"
            confidence = Decimal("0.85")
        else:
            action = "unknown_action"
            target = None
            confidence = Decimal("0.40")

        entities = ExtractedEntities(
            amount=amount,
            currency=currency,
            merchant=merchant,
            target_id=context_metadata.get("target_id"),
            recipient=context_metadata.get("recipient"),
        )

        return StructuredIntent(
            intent_id=uuid.uuid4(),
            action=action,
            target=target,
            entities=entities,
            parameters={"raw_prompt_length": len(sanitized_text)},
            constraints=context_metadata.get("constraints", {}),
            confidence=confidence,
            source="rule_based_provider",
            extracted_at=datetime.utcnow(),
        )


class IntentExtractionService:
    """Application service orchestrating Intent Extraction (Phase 140)."""

    def __init__(self, provider: BaseIntentExtractorProvider | None = None) -> None:
        if provider is not None:
            self.provider = provider
        else:
            try:
                from app.application.services.llm_intent_extractor_provider import (
                    LLMIntentExtractorProvider,
                )
                self.provider = LLMIntentExtractorProvider()
            except Exception:
                self.provider = RuleBasedIntentExtractorProvider()


    async def extract_intent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request_text: str,
        context_metadata: dict[str, Any] | None = None,
    ) -> IntentExtractionResponse:
        """Extract structured intent within verified tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            IntentExtractionError: if extraction fails.
        """
        # 1. IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        meta = context_metadata or {}
        try:
            intent = await self.provider.extract(request_text, meta)
        except Exception as exc:
            logger.error("Intent extraction failed", exc_info=exc)
            raise IntentExtractionError(f"Failed to extract intent: {exc}") from exc

        logger.info(
            "Intent extracted successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "action": intent.action,
                "confidence": str(intent.confidence),
            },
        )

        return IntentExtractionResponse(
            agent_id=agent_id,
            tenant_id=tenant_id,
            extracted_intent=intent,
            extraction_metadata={"provider": intent.source},
        )
