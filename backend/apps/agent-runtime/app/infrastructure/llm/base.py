"""Abstract ILLMProvider interface definition."""

from __future__ import annotations

import abc
from typing import TypeVar
from pydantic import BaseModel

from app.infrastructure.llm.schemas import LLMRequest, LLMResponse, StructuredLLMResponse

T = TypeVar("T", bound=BaseModel)


class ILLMProvider(abc.ABC):
    """Abstract interface for ATIM LLM providers.

    INVARIANT: Providers must NEVER execute financial transactions or alter policies.
    """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Canonical provider identifier e.g. 'openai' or 'anthropic'."""
        ...

    @property
    @abc.abstractmethod
    def default_model(self) -> str:
        """Default model identifier e.g. 'gpt-4o-mini'."""
        ...

    @abc.abstractmethod
    async def generate_text(
        self,
        request: LLMRequest,
        model: str | None = None,
    ) -> LLMResponse:
        """Generate raw text response from provider."""
        ...

    @abc.abstractmethod
    async def generate_structured(
        self,
        schema: type[T],
        request: LLMRequest,
        model: str | None = None,
        max_retries: int = 3,
    ) -> StructuredLLMResponse[T]:
        """Generate type-safe Pydantic structured output with validation retries."""
        ...

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Verify API key validity and provider availability."""
        ...
