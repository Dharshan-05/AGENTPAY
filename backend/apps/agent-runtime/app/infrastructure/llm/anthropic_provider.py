"""Anthropic Provider implementation for ATIM."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, TypeVar
from pydantic import BaseModel, ValidationError

try:
    import anthropic
    from anthropic import AsyncAnthropic
except ImportError:  # pragma: no cover
    anthropic = None
    AsyncAnthropic = None

from app.infrastructure.llm.base import ILLMProvider
from app.infrastructure.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMValidationError,
)
from app.infrastructure.llm.schemas import (
    LLMRequest,
    LLMResponse,
    LLMTokenUsage,
    StructuredLLMResponse,
)

logger = logging.getLogger("agentpay.atim.llm.anthropic")

T = TypeVar("T", bound=BaseModel)

# Approximate pricing per 1M tokens (USD)
ANTHROPIC_PRICING = {
    "claude-3-5-haiku-20241022": {"prompt": 0.80 / 1e6, "completion": 4.00 / 1e6},
    "claude-3-5-sonnet-20241022": {"prompt": 3.00 / 1e6, "completion": 15.00 / 1e6},
}


class AnthropicProvider(ILLMProvider):
    """Production Anthropic LLM Provider supporting structured outputs and retry logic."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "claude-3-5-haiku-20241022",
    ) -> None:
        self._api_key = api_key
        self._default_model = default_model
        self._client: Any = None

        if AsyncAnthropic and api_key and api_key.strip():
            self._client = AsyncAnthropic(api_key=api_key.strip())

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return self._default_model

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        rates = ANTHROPIC_PRICING.get(model, ANTHROPIC_PRICING["claude-3-5-haiku-20241022"])
        cost = (prompt_tokens * rates["prompt"]) + (completion_tokens * rates["completion"])
        return round(cost, 6)

    async def generate_text(
        self,
        request: LLMRequest,
        model: str | None = None,
    ) -> LLMResponse:
        """Execute raw text completion request via Anthropic Messages API."""
        if not self._client:
            raise LLMAuthenticationError(
                "Anthropic API key is missing or client is uninitialized.",
                provider=self.provider_name,
                model=model or self.default_model,
            )

        target_model = model or self.default_model
        start_time = time.perf_counter()

        try:
            res = await self._client.messages.create(
                model=target_model,
                max_tokens=request.max_tokens or 1024,
                temperature=request.temperature,
                system=request.system_prompt or "",
                messages=[{"role": "user", "content": request.prompt}],
                timeout=request.timeout_seconds,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            content = ""
            if res.content and len(res.content) > 0:
                content = res.content[0].text if hasattr(res.content[0], "text") else str(res.content[0])

            prompt_tokens = res.usage.input_tokens if res.usage else 0
            completion_tokens = res.usage.output_tokens if res.usage else 0
            total_tokens = prompt_tokens + completion_tokens
            cost = self._calculate_cost(target_model, prompt_tokens, completion_tokens)

            return LLMResponse(
                correlation_id=request.correlation_id,
                provider=self.provider_name,
                model=target_model,
                content=content,
                latency_ms=round(elapsed_ms, 2),
                usage=LLMTokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost_usd=cost,
                ),
                finish_reason=res.stop_reason or "end_turn",
            )
        except Exception as exc:
            self._handle_exception(exc, target_model)
            raise

    async def generate_structured(
        self,
        schema: type[T],
        request: LLMRequest,
        model: str | None = None,
        max_retries: int = 3,
    ) -> StructuredLLMResponse[T]:
        """Generate structured Pydantic model with validation retries."""
        if not self._client:
            raise LLMAuthenticationError(
                "Anthropic API key is missing or client is uninitialized.",
                provider=self.provider_name,
                model=model or self.default_model,
            )

        target_model = model or self.default_model
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        system_instruction = (
            f"{request.system_prompt or ''}\n\n"
            f"CRITICAL: You MUST respond ONLY with a valid JSON object matching this JSON Schema:\n"
            f"{schema_json}\n"
            f"Do NOT wrap JSON in markdown backticks or add commentary. Return ONLY the raw JSON object."
        ).strip()

        messages: list[dict[str, str]] = [
            {"role": "user", "content": request.prompt},
        ]

        attempt = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        start_time = time.perf_counter()

        while attempt < max_retries:
            attempt += 1
            try:
                res = await self._client.messages.create(
                    model=target_model,
                    max_tokens=request.max_tokens or 1024,
                    temperature=request.temperature,
                    system=system_instruction,
                    messages=messages,
                    timeout=request.timeout_seconds,
                )

                if res.usage:
                    total_prompt_tokens += res.usage.input_tokens
                    total_completion_tokens += res.usage.output_tokens

                raw_text = ""
                if res.content and len(res.content) > 0:
                    raw_text = res.content[0].text if hasattr(res.content[0], "text") else str(res.content[0])

                clean_text = raw_text.strip()
                if clean_text.startswith("```"):
                    clean_text = clean_text.split("```")[1]
                    if clean_text.startswith("json"):
                        clean_text = clean_text[4:]
                    clean_text = clean_text.strip()

                try:
                    parsed_json = json.loads(clean_text)
                    instance = schema.model_validate(parsed_json)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                    cost = self._calculate_cost(
                        target_model, total_prompt_tokens, total_completion_tokens
                    )

                    return StructuredLLMResponse[T](
                        correlation_id=request.correlation_id,
                        provider=self.provider_name,
                        model=target_model,
                        data=instance,
                        raw_content=raw_text,
                        latency_ms=round(elapsed_ms, 2),
                        usage=LLMTokenUsage(
                            prompt_tokens=total_prompt_tokens,
                            completion_tokens=total_completion_tokens,
                            total_tokens=total_prompt_tokens + total_completion_tokens,
                            estimated_cost_usd=cost,
                        ),
                        retry_count=attempt - 1,
                        validation_status="VALIDATED",
                    )
                except (json.JSONDecodeError, ValidationError) as val_err:
                    logger.warning(
                        "Anthropic output validation failed (attempt %d/%d): %s",
                        attempt,
                        max_retries,
                        val_err,
                    )
                    if attempt >= max_retries:
                        raise LLMValidationError(
                            f"Structured output validation failed after {max_retries} attempts: {val_err}",
                            raw_response=raw_text,
                            provider=self.provider_name,
                            model=target_model,
                        ) from val_err

                    messages.append({"role": "assistant", "content": raw_text})
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Your response failed validation:\n{val_err}\nPlease fix errors and output valid JSON conforming strictly to the schema.",
                        }
                    )
            except Exception as exc:
                if isinstance(exc, (LLMValidationError, LLMAuthenticationError)):
                    raise
                self._handle_exception(exc, target_model)
                raise

        raise LLMValidationError(
            f"Failed to generate structured output after {max_retries} retries.",
            provider=self.provider_name,
            model=target_model,
        )

    async def health_check(self) -> bool:
        """Check API key validity by testing small request."""
        if not self._client:
            return False
        try:
            res = await self._client.messages.create(
                model=self.default_model,
                max_tokens=5,
                messages=[{"role": "user", "content": "ping"}],
                timeout=5.0,
            )
            return bool(res.content)
        except Exception:
            return False

    def _handle_exception(self, exc: Exception, model: str) -> None:
        if anthropic is not None:
            if isinstance(exc, anthropic.AuthenticationError):
                raise LLMAuthenticationError(
                    f"Anthropic Authentication Failed: {exc}",

                    provider=self.provider_name,
                    model=model,
                ) from exc
            if isinstance(exc, anthropic.RateLimitError):
                raise LLMRateLimitError(
                    f"Anthropic Rate Limit Exceeded: {exc}",
                    provider=self.provider_name,
                    model=model,
                ) from exc
            if isinstance(exc, anthropic.APITimeoutError):
                raise LLMTimeoutError(
                    f"Anthropic Request Timed Out: {exc}",
                    provider=self.provider_name,
                    model=model,
                ) from exc
        raise LLMProviderError(
            f"Anthropic Provider Error: {exc}",
            provider=self.provider_name,
            model=model,
        ) from exc
