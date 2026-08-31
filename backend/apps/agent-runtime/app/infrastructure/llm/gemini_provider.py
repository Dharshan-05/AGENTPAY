"""Google Gemini Provider implementation for ATIM (Free-Tier API Support)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

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

logger = logging.getLogger("agentpay.atim.llm.gemini")

T = TypeVar("T", bound=BaseModel)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(ILLMProvider):
    """Production Google Gemini LLM Provider supporting Free-Tier API execution and structured output."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gemini-3.6-flash",
    ) -> None:
        self._api_key = api_key
        self._default_model = default_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return self._default_model

    async def health_check(self) -> bool:
        if not self._api_key or not self._api_key.strip():
            return False
        try:
            url = f"{GEMINI_BASE_URL}/models/{self._default_model}?key={self._api_key.strip()}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                return resp.status_code == 200
        except Exception:
            return False

    def _handle_exception(self, exc: Exception, model: str) -> None:
        if isinstance(exc, (LLMAuthenticationError, LLMRateLimitError, LLMTimeoutError, LLMValidationError, LLMProviderError)):
            raise exc

        msg = str(exc)
        if isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code
            if status_code in (401, 403):
                raise LLMAuthenticationError(f"Gemini Auth Error ({status_code}): {msg}") from exc
            if status_code == 429 or "RESOURCE_EXHAUSTED" in msg or "QUOTA" in msg:
                raise LLMRateLimitError(f"Gemini Rate Limit / Quota Exceeded ({status_code}): {msg}") from exc
            if status_code in (408, 504):
                raise LLMTimeoutError(f"Gemini Timeout ({status_code}): {msg}") from exc
            raise LLMProviderError(f"Gemini Provider Error ({status_code}): {msg}") from exc
        if isinstance(exc, httpx.TimeoutException):
            raise LLMTimeoutError(f"Gemini Request Timeout: {msg}") from exc

        raise LLMProviderError(f"Gemini Execution Failed on model '{model}': {msg}") from exc

    async def generate_text(
        self,
        request: LLMRequest,
        model: str | None = None,
    ) -> LLMResponse:
        if not self._api_key or not self._api_key.strip():
            raise LLMAuthenticationError("GEMINI_API_KEY is not configured.")

        target_model = model or self._default_model
        start_time = time.perf_counter()

        url = f"{GEMINI_BASE_URL}/models/{target_model}:generateContent?key={self._api_key.strip()}"
        payload = {
            "contents": [{"parts": [{"text": request.prompt}]}],
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens or 1024,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=request.timeout_seconds or 30.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            latency_ms = (time.perf_counter() - start_time) * 1000.0

            candidates = data.get("candidates", [])
            if not candidates:
                raise LLMProviderError("Gemini returned empty candidates list.")

            content_parts = candidates[0].get("content", {}).get("parts", [])
            text_response = content_parts[0].get("text", "") if content_parts else ""

            usage_meta = data.get("usageMetadata", {})
            prompt_tokens = usage_meta.get("promptTokenCount", 0)
            comp_tokens = usage_meta.get("candidatesTokenCount", 0)
            total_tokens = usage_meta.get("totalTokenCount", prompt_tokens + comp_tokens)

            return LLMResponse(
                correlation_id=request.correlation_id,
                provider=self.provider_name,
                model=target_model,
                content=text_response,
                latency_ms=latency_ms,
                finish_reason="stop",
                usage=LLMTokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=comp_tokens,
                    total_tokens=total_tokens,
                    estimated_cost_usd=0.0,  # Free tier
                ),
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
        if not self._api_key or not self._api_key.strip():
            raise LLMAuthenticationError("GEMINI_API_KEY is not configured.")

        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        system_instruction = (
            f"You MUST respond ONLY with a valid JSON object strictly matching this JSON schema:\n{schema_json}\n"
            f"Do not include markdown code block formatting or extra commentary."
        )

        enhanced_prompt = f"{system_instruction}\n\nUSER PROMPT:\n{request.prompt}"
        structured_req = LLMRequest(
            prompt=enhanced_prompt,
            correlation_id=request.correlation_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            timeout_seconds=request.timeout_seconds,
        )

        last_raw_response: LLMResponse | None = None
        for attempt in range(1, max_retries + 1):
            raw_response = await self.generate_text(structured_req, model=model)
            last_raw_response = raw_response

            clean_text = raw_response.content.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            try:
                parsed_json = json.loads(clean_text)
                validated_data = schema.model_validate(parsed_json)
                return StructuredLLMResponse(
                    correlation_id=request.correlation_id,
                    provider=self.provider_name,
                    model=model or self._default_model,
                    data=validated_data,
                    raw_content=raw_response.content,
                    latency_ms=raw_response.latency_ms,
                    usage=raw_response.usage,
                    retry_count=attempt - 1,
                )
            except (json.JSONDecodeError, ValidationError) as err:
                logger.warning("Gemini structured output validation failed (attempt %d/%d): %s", attempt, max_retries, err)

        raise LLMValidationError(
            f"Failed to generate structured output matching schema '{schema.__name__}' after {max_retries} attempts. "
            f"Last raw response: {last_raw_response.content if last_raw_response else None}"
        )
