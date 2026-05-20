"""
Anthropic Claude LLM provider implementation.

Requires:
    pip install se-principles-mcp[anthropic]

Environment:
    ANTHROPIC_API_KEY — Your Anthropic API key
    SE_MCP_MODEL     — Optional model override (default: claude-sonnet-4-20250514)
"""

from __future__ import annotations

import os

from se_principles_mcp.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """LLM provider using Anthropic's Claude API."""

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        try:
            import anthropic  # noqa: F401
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required for the Anthropic provider.\n"
                "Install it with: pip install se-principles-mcp[anthropic]"
            )

        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set.\n"
                "Get your key at: https://console.anthropic.com/settings/keys"
            )

        self._model = model or os.environ.get("SE_MCP_MODEL", "claude-sonnet-4-20250514")
        self._client = anthropic.Anthropic(api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response using Anthropic's Messages API."""
        response = self._client.messages.create(
            model=self._model,
            max_tokens=8096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )
