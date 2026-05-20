"""
OpenAI GPT LLM provider implementation.

Requires:
    pip install se-lifecycle-mcp[openai]

Environment:
    OPENAI_API_KEY - Your OpenAI API key
    SE_MCP_MODEL   - Optional model override (default: gpt-4o)
"""

from __future__ import annotations

import os

from se_lifecycle_mcp.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """LLM provider using OpenAI's Chat Completions API."""

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        try:
            import openai  # noqa: F401
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for the OpenAI provider.\n"
                "Install it with: pip install se-lifecycle-mcp[openai]"
            )

        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set.\n"
                "Get your key at: https://platform.openai.com/api-keys"
            )

        self._model = model or os.environ.get("SE_MCP_MODEL", "gpt-4o")
        self._client = openai.OpenAI(api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response using OpenAI's Chat Completions API."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=8096,
        )

        return response.choices[0].message.content or ""
