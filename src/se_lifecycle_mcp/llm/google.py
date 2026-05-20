"""
Google Gemini LLM provider implementation.

Requires:
    pip install se-lifecycle-mcp[google]

Environment:
    GOOGLE_API_KEY - Your Google AI API key
    SE_MCP_MODEL   - Optional model override (default: gemini-2.5-flash)
"""

from __future__ import annotations

import os

from se_lifecycle_mcp.llm.base import LLMProvider


class GoogleProvider(LLMProvider):
    """LLM provider using Google's Gemini API."""

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        try:
            from google import genai  # noqa: F401
        except ImportError:
            raise ImportError(
                "The 'google-genai' package is required for the Google provider.\n"
                "Install it with: pip install se-lifecycle-mcp[google]"
            )

        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set.\n"
                "Get your key at: https://aistudio.google.com/apikey"
            )

        self._model = model or os.environ.get("SE_MCP_MODEL", "gemini-2.5-flash")
        self._client = genai.Client(api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "Google"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response using Google's Gemini API."""
        from google.genai import types

        response = self._client.models.generate_content(
            model=self._model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=8096,
            ),
        )

        return response.text or ""
