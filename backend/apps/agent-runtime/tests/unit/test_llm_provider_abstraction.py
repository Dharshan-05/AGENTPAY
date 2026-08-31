"""Unit tests for ATIM LLM provider abstraction and structured output generation."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, Field

from app.infrastructure.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
    LLMValidationError,
)
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.llm.anthropic_provider import AnthropicProvider
from app.infrastructure.llm.schemas import LLMRequest


class MockSampleSchema(BaseModel):
    action: str = Field(description="Action name")
    amount: float = Field(description="Amount")


@pytest.mark.asyncio
async def test_openai_provider_uninitialized_raises_auth_error():
    """Test that OpenAIProvider raises LLMAuthenticationError when no API key is provided."""
    provider = OpenAIProvider(api_key=None)
    assert provider.provider_name == "openai"
    assert provider.default_model == "gpt-4o-mini"
    assert await provider.health_check() is False

    req = LLMRequest(prompt="Test prompt")
    with pytest.raises(LLMAuthenticationError):
        await provider.generate_text(req)

    with pytest.raises(LLMAuthenticationError):
        await provider.generate_structured(MockSampleSchema, req)


@pytest.mark.asyncio
async def test_anthropic_provider_uninitialized_raises_auth_error():
    """Test that AnthropicProvider raises LLMAuthenticationError when no API key is provided."""
    provider = AnthropicProvider(api_key=None)
    assert provider.provider_name == "anthropic"
    assert provider.default_model == "claude-3-5-haiku-20241022"
    assert await provider.health_check() is False

    req = LLMRequest(prompt="Test prompt")
    with pytest.raises(LLMAuthenticationError):
        await provider.generate_text(req)

    with pytest.raises(LLMAuthenticationError):
        await provider.generate_structured(MockSampleSchema, req)
