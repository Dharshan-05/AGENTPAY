"""LLMRouter for provider failover, retry handling, and token accounting."""

from __future__ import annotations

import logging
from typing import TypeVar
from pydantic import BaseModel

from app.core.config import Settings
from app.infrastructure.llm.anthropic_provider import AnthropicProvider
from app.infrastructure.llm.base import ILLMProvider
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.gemini_provider import GeminiProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.llm.schemas import (
    LLMRequest,
    LLMResponse,
    StructuredLLMResponse,
)

logger = logging.getLogger("agentpay.atim.llm.router")

T = TypeVar("T", bound=BaseModel)


class LLMRouter:
    """Production LLM Router orchestrating multi-provider failover and structured generation."""

    def __init__(
        self,
        settings: Settings | None = None,
        primary_provider: ILLMProvider | None = None,
        secondary_provider: ILLMProvider | None = None,
        tertiary_provider: ILLMProvider | None = None,
    ) -> None:
        self.settings = settings or Settings()

        openai_key = (
            self.settings.openai_api_key.get_secret_value()
            if self.settings.openai_api_key
            else None
        )
        anthropic_key = (
            self.settings.anthropic_api_key.get_secret_value()
            if self.settings.anthropic_api_key
            else None
        )
        gemini_key = (
            self.settings.gemini_api_key.get_secret_value()
            if getattr(self.settings, "gemini_api_key", None)
            else None
        )

        self.primary_provider = primary_provider or OpenAIProvider(
            api_key=openai_key,
            default_model=self.settings.llm_primary_model,
        )
        self.secondary_provider = secondary_provider or AnthropicProvider(
            api_key=anthropic_key,
            default_model=self.settings.llm_secondary_model,
        )
        self.tertiary_provider = tertiary_provider or GeminiProvider(
            api_key=gemini_key,
            default_model="gemini-1.5-flash",
        )

    async def generate_structured(
        self,
        schema: type[T],
        request: LLMRequest,
        max_retries: int | None = None,
    ) -> StructuredLLMResponse[T]:
        """Execute structured generation with primary -> secondary failover.

        Raises:
            LLMProviderError: if all configured LLM providers fail or are disabled.
        """
        if not self.settings.llm_enabled:
            raise LLMProviderError("LLM generation is disabled via configuration (LLM_ENABLED=false).")

        retries = max_retries if max_retries is not None else self.settings.llm_max_retries

        # 1. Attempt Primary Provider
        try:
            logger.info(
                "Routing request %s to primary provider '%s' (%s)",
                request.correlation_id,
                self.primary_provider.provider_name,
                self.primary_provider.default_model,
            )
            return await self.primary_provider.generate_structured(
                schema=schema,
                request=request,
                model=self.settings.llm_primary_model,
                max_retries=retries,
            )
        except Exception as primary_exc:
            logger.warning(
                "Primary provider '%s' failed for req %s: %s. Attempting failover to secondary.",
                self.primary_provider.provider_name,
                request.correlation_id,
                primary_exc,
            )

        # 2. Attempt Secondary Provider
        try:
            logger.info(
                "Failing over request %s to secondary provider '%s' (%s)",
                request.correlation_id,
                self.secondary_provider.provider_name,
                self.secondary_provider.default_model,
            )
            return await self.secondary_provider.generate_structured(
                schema=schema,
                request=request,
                model=self.settings.llm_secondary_model,
                max_retries=retries,
            )
        except Exception as secondary_exc:
            logger.error(
                "Secondary provider '%s' failed for req %s: %s. All LLM providers exhausted.",
                self.secondary_provider.provider_name,
                request.correlation_id,
                secondary_exc,
            )

        raise LLMProviderError(
            f"All configured LLM providers failed for request {request.correlation_id}.",
            provider="all",
        )

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Execute text generation with primary -> secondary failover."""
        if not self.settings.llm_enabled:
            raise LLMProviderError("LLM generation is disabled via configuration (LLM_ENABLED=false).")

        try:
            return await self.primary_provider.generate_text(
                request=request,
                model=self.settings.llm_primary_model,
            )
        except Exception as primary_exc:
            logger.warning(
                "Primary provider text gen failed for req %s: %s. Attempting secondary.",
                request.correlation_id,
                primary_exc,
            )

        try:
            return await self.secondary_provider.generate_text(
                request=request,
                model=self.settings.llm_secondary_model,
            )
        except Exception as secondary_exc:
            logger.error(
                "Secondary provider text gen failed for req %s: %s.",
                request.correlation_id,
                secondary_exc,
            )

        raise LLMProviderError(f"All LLM providers failed for text request {request.correlation_id}.")
