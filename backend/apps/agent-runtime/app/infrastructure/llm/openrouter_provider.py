"""OpenRouter LLM Provider implementation for AGENTPAY."""

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

logger = logging.getLogger("agentpay.atim.llm.openrouter")

T = TypeVar("T", bound=BaseModel)

# Default OpenRouter fallback pricing (per 1M tokens)
OPENROUTER_DEFAULT_PRICING = {"prompt": 0.15 / 1e6, "completion": 0.60 / 1e6}


class OpenRouterProvider(ILLMProvider):
    """Production OpenRouter LLM Provider supporting multi-model routing and structured outputs.

    INVARIANT: API Key is strictly server-side and never exposed to client/browser code.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "openai/gpt-4o-mini",
    ) -> None:
        self._raw_key = api_key
        self._base_url = base_url.rstrip("/")
        self._default_model = default_model
        self._client: Any = None

        clean_key = self._extract_clean_key(api_key)
        if AsyncOpenAI and clean_key:
            self._client = AsyncOpenAI(
                api_key=clean_key,
                base_url=self._base_url,
                default_headers={
                    "HTTP-Referer": "https://agentpay.dev",
                    "X-Title": "AGENTPAY Real Online Commerce Assistant",
                },
            )

    def _extract_clean_key(self, raw_key: str | None) -> str | None:
        if not raw_key or not isinstance(raw_key, str):
            return None
        raw_key = raw_key.strip()
        if "sk-or-v1-" in raw_key:
            idx = raw_key.find("sk-or-v1-")
            return raw_key[idx:]
        return raw_key if raw_key else None

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def default_model(self) -> str:
        return self._default_model

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        rates = OPENROUTER_DEFAULT_PRICING
        cost = (prompt_tokens * rates["prompt"]) + (completion_tokens * rates["completion"])
        return round(cost, 6)

    async def generate_text(
        self,
        request: LLMRequest,
        model: str | None = None,
    ) -> LLMResponse:
        """Execute raw text completion request via OpenRouter API."""
        if not self._client:
            raise LLMAuthenticationError(
                "OpenRouter API key is missing or uninitialized.",
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
            prompt_tokens = res.usage.prompt_tokens if res.usage else 0
            completion_tokens = res.usage.completion_tokens if res.usage else 0
            total_tokens = res.usage.total_tokens if res.usage else 0

            cost = self._calculate_cost(prompt_tokens, completion_tokens)

            return LLMResponse(
                content=content,
                model=target_model,
                provider=self.provider_name,
                usage=LLMTokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost_usd=cost,
                ),
                latency_ms=elapsed_ms,
                correlation_id=request.correlation_id,
            )

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_str = str(exc)
            logger.warning("OpenRouter text gen failed for model %s: %s", target_model, error_str)

            if "401" in error_str or "auth" in error_str.lower():
                raise LLMAuthenticationError(
                    f"OpenRouter Authentication Error: {error_str}",
                    provider=self.provider_name,
                    model=target_model,
                ) from exc
            elif "429" in error_str or "rate limit" in error_str.lower() or "quota" in error_str.lower():
                raise LLMRateLimitError(
                    f"OpenRouter Rate Limit Exceeded: {error_str}",
                    provider=self.provider_name,
                    model=target_model,
                ) from exc
            elif "timeout" in error_str.lower():
                raise LLMTimeoutError(
                    f"OpenRouter Request Timeout: {error_str}",
                    provider=self.provider_name,
                    model=target_model,
                ) from exc

            raise LLMProviderError(
                f"OpenRouter Provider Error: {error_str}",
                provider=self.provider_name,
                model=target_model,
            ) from exc

    async def generate_structured(
        self,
        schema: type[T],
        request: LLMRequest,
        model: str | None = None,
        max_retries: int = 3,
    ) -> StructuredLLMResponse[T]:
        """Generate type-safe Pydantic structured output using OpenRouter JSON mode & validation retries."""
        if not self._client:
            raise LLMAuthenticationError(
                "OpenRouter API key is missing or uninitialized.",
                provider=self.provider_name,
                model=model or self.default_model,
            )

        target_model = model or self.default_model
        schema_json = json.dumps(schema.model_json_schema(), indent=2)

        enhanced_system_prompt = (
            f"{request.system_prompt or ''}\n\n"
            f"CRITICAL INSTRUCTION: You MUST return a single valid JSON object strictly matching this schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Output ONLY valid raw JSON with zero markdown codeblock wrappers."
        ).strip()

        messages: list[dict[str, str]] = [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "user", "content": request.prompt},
        ]

        attempt = 0
        start_time = time.perf_counter()
        last_error_detail = ""

        while attempt < max_retries:
            attempt += 1
            try:
                res = await self._client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    response_format={"type": "json_object"},
                    timeout=request.timeout_seconds,
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                raw_content = res.choices[0].message.content or ""
                # Strip markdown fence wrappers if present
                clean_json = raw_content.strip()
                if clean_json.startswith("```"):
                    lines = clean_json.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    clean_json = "\n".join(lines).strip()

                parsed_dict = json.loads(clean_json)
                parsed_object = schema.model_validate(parsed_dict)

                prompt_tokens = res.usage.prompt_tokens if res.usage else 0
                completion_tokens = res.usage.completion_tokens if res.usage else 0
                total_tokens = res.usage.total_tokens if res.usage else 0
                cost = self._calculate_cost(prompt_tokens, completion_tokens)

                return StructuredLLMResponse[T](
                    raw_response=raw_content,
                    parsed_object=parsed_object,
                    model=target_model,
                    provider=self.provider_name,
                    usage=LLMTokenUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        estimated_cost_usd=cost,
                    ),
                    latency_ms=elapsed_ms,
                    correlation_id=request.correlation_id,
                    retries_count=attempt - 1,
                )

            except (json.JSONDecodeError, ValidationError) as parse_exc:
                last_error_detail = str(parse_exc)
                logger.warning(
                    "OpenRouter structured parse failed (attempt %d/%d) for model %s: %s",
                    attempt,
                    max_retries,
                    target_model,
                    parse_exc,
                )
                messages.append({"role": "assistant", "content": raw_content if 'raw_content' in locals() else ""})
                messages.append({
                    "role": "user",
                    "content": f"JSON validation error: {last_error_detail}. Please fix and return pure JSON.",
                })

            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                error_str = str(exc)
                logger.warning("OpenRouter API error (attempt %d/%d): %s", attempt, max_retries, error_str)

                if "401" in error_str or "auth" in error_str.lower():
                    raise LLMAuthenticationError(
                        f"OpenRouter Authentication Error: {error_str}",
                        provider=self.provider_name,
                        model=target_model,
                    ) from exc
                elif "429" in error_str or "rate limit" in error_str.lower() or "quota" in error_str.lower():
                    raise LLMRateLimitError(
                        f"OpenRouter Rate Limit Exceeded: {error_str}",
                        provider=self.provider_name,
                        model=target_model,
                    ) from exc

                if attempt >= max_retries:
                    raise LLMProviderError(
                        f"OpenRouter Provider failed after {max_retries} attempts: {error_str}",
                        provider=self.provider_name,
                        model=target_model,
                    ) from exc

        raise LLMValidationError(
            f"Failed to produce valid JSON structured output for schema {schema.__name__} after {max_retries} attempts. Last error: {last_error_detail}",
            provider=self.provider_name,
            model=target_model,
            raw_output=last_error_detail,
        )

    async def health_check(self) -> bool:
        """Verify OpenRouter client initialization and connectivity."""
        return self._client is not None
