"""OpenAI Provider implementation for ATIM."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, TypeVar
from pydantic import BaseModel, ValidationError

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    openai = None
    AsyncOpenAI = None

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

logger = logging.getLogger("agentpay.atim.llm.openai")

T = TypeVar("T", bound=BaseModel)

# Approximate pricing per 1M tokens (USD)
OPENAI_PRICING = {
    "gpt-4o-mini": {"prompt": 0.15 / 1e6, "completion": 0.60 / 1e6},
    "gpt-4o": {"prompt": 2.50 / 1e6, "completion": 10.00 / 1e6},
    "gpt-3.5-turbo": {"prompt": 0.50 / 1e6, "completion": 1.50 / 1e6},
}


class OpenAIProvider(ILLMProvider):
    """Production OpenAI LLM Provider supporting structured outputs and retry logic."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        self._api_key = api_key
        self._default_model = default_model
        self._client: Any = None

        if AsyncOpenAI and api_key and api_key.strip():
            self._client = AsyncOpenAI(api_key=api_key.strip())

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._default_model

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        rates = OPENAI_PRICING.get(model, OPENAI_PRICING["gpt-4o-mini"])
        cost = (prompt_tokens * rates["prompt"]) + (completion_tokens * rates["completion"])
        return round(cost, 6)

    async def generate_text(
        self,
        request: LLMRequest,
        model: str | None = None,
    ) -> LLMResponse:
        """Execute raw text completion request via OpenAI ChatCompletions API."""
        if not self._client:
            raise LLMAuthenticationError(
                "OpenAI API key is missing or client is uninitialized.",
                provider=self.provider_name,
                model=model or self.default_model,
            )

        target_model = model or self.default_model
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        start_time = time.perf_counter()
        try:
            res = await self._client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                timeout=request.timeout_seconds,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            content = res.choices[0].message.content or ""
            usage_obj = res.usage
            prompt_tokens = usage_obj.prompt_tokens if usage_obj else 0
            completion_tokens = usage_obj.completion_tokens if usage_obj else 0
            total_tokens = usage_obj.total_tokens if usage_obj else 0
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
                finish_reason=res.choices[0].finish_reason or "stop",
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
        """Generate structured Pydantic model with validation retries (Instructor pattern)."""
        if not self._client:
            raise LLMAuthenticationError(
                "OpenAI API key is missing or client is uninitialized.",
                provider=self.provider_name,
                model=model or self.default_model,
            )

        target_model = model or self.default_model
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        system_instruction = (
            f"{request.system_prompt or ''}\n\n"
            f"CRITICAL: You MUST respond ONLY with a valid JSON object matching this JSON Schema:\n"
            f"{schema_json}\n"
            f"Do NOT wrap JSON in markdown backticks or add commentary."
        ).strip()

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": request.prompt},
        ]

        attempt = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        start_time = time.perf_counter()

        while attempt < max_retries:
            attempt += 1
            try:
                res = await self._client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=request.temperature,
                    response_format={"type": "json_object"},
                    timeout=request.timeout_seconds,
                )

                if res.usage:
                    total_prompt_tokens += res.usage.prompt_tokens
                    total_completion_tokens += res.usage.completion_tokens

                raw_text = res.choices[0].message.content or "{}"
                # Clean potential markdown wrapping
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
                        "OpenAI output validation failed (attempt %d/%d): %s",
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

                    # Feed validation error back to LLM for retry
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
            res = await self._client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                timeout=5.0,
            )
            return bool(res.choices)
        except Exception:
            return False

    def _handle_exception(self, exc: Exception, model: str) -> None:
        if openai is not None:
            if isinstance(exc, openai.AuthenticationError):
                raise LLMAuthenticationError(
                    f"OpenAI Authentication Failed: {exc}",
                    provider=self.provider_name,
                    model=model,
                ) from exc
            if isinstance(exc, openai.RateLimitError):
                raise LLMRateLimitError(
                    f"OpenAI Rate Limit Exceeded: {exc}",
                    provider=self.provider_name,
                    model=model,
                ) from exc
            if isinstance(exc, openai.APITimeoutError):
                raise LLMTimeoutError(
                    f"OpenAI Request Timed Out: {exc}",
                    provider=self.provider_name,
                    model=model,
                ) from exc
        raise LLMProviderError(
            f"OpenAI Provider Error: {exc}",
            provider=self.provider_name,
            model=model,
        ) from exc
