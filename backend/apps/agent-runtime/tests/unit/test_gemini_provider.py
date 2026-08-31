"""Unit tests for ATIM Gemini provider implementation."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, Field

from app.infrastructure.llm.exceptions import LLMAuthenticationError
from app.infrastructure.llm.gemini_provider import GeminiProvider
from app.infrastructure.llm.schemas import LLMRequest


class MockSampleSchema(BaseModel):
    action: str = Field(description="Action name")
    status: str = Field(description="Execution status")


@pytest.mark.asyncio
async def test_gemini_provider_uninitialized_raises_auth_error():
    """Test that GeminiProvider raises LLMAuthenticationError when no API key is provided."""
    provider = GeminiProvider(api_key=None)
    assert provider.provider_name == "gemini"
    assert provider.default_model == "gemini-3.6-flash"
    assert await provider.health_check() is False

    req = LLMRequest(prompt="Test prompt")
    with pytest.raises(LLMAuthenticationError):
        await provider.generate_text(req)

    with pytest.raises(LLMAuthenticationError):
        await provider.generate_structured(MockSampleSchema, req)


@pytest.mark.asyncio
async def test_gemini_provider_initialization_with_key():
    """Test GeminiProvider initialization properties."""
    provider = GeminiProvider(api_key="test_dummy_key", default_model="gemini-3.6-flash")
    assert provider.provider_name == "gemini"
    assert provider.default_model == "gemini-3.6-flash"
