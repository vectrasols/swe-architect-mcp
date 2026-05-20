"""
LLM Provider Factory
====================
Factory function that creates the appropriate LLM provider based on
environment configuration. Supports explicit selection via SE_MCP_PROVIDER
and auto-detection from available API keys.

Design Patterns: Factory Method + Strategy
Principles: Open/Closed (add new providers without modifying existing code)
"""

from __future__ import annotations

import os
import sys

from se_principles_mcp.llm.base import LLMProvider


# Provider registry — maps provider names to their module + class
_PROVIDER_REGISTRY: dict[str, tuple[str, str]] = {
    "anthropic": ("se_principles_mcp.llm.anthropic", "AnthropicProvider"),
    "openai": ("se_principles_mcp.llm.openai", "OpenAIProvider"),
    "google": ("se_principles_mcp.llm.google", "GoogleProvider"),
}

# API key env vars for auto-detection, checked in priority order
_API_KEY_MAP: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
}


def create_provider(
    provider_name: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> LLMProvider:
    """Create an LLM provider instance.

    Resolution order:
        1. Explicit `provider_name` argument
        2. `SE_MCP_PROVIDER` environment variable
        3. Auto-detect from available API keys (first found wins)

    Args:
        provider_name: Explicit provider name ('anthropic', 'openai', 'google').
        model: Override the default model for the chosen provider.
        api_key: Override the API key (otherwise read from env).

    Returns:
        A configured LLMProvider instance.

    Raises:
        ValueError: If no provider can be determined or the provider name is unknown.
    """
    # Step 1: Resolve provider name
    name = (
        provider_name
        or os.environ.get("SE_MCP_PROVIDER", "").strip().lower()
        or _auto_detect_provider()
    )

    if not name:
        raise ValueError(
            "No LLM provider configured. Set one of the following environment variables:\n"
            "  • ANTHROPIC_API_KEY  (for Anthropic Claude)\n"
            "  • OPENAI_API_KEY    (for OpenAI GPT)\n"
            "  • GOOGLE_API_KEY    (for Google Gemini)\n"
            "\n"
            "Or explicitly set SE_MCP_PROVIDER=anthropic|openai|google\n"
            "\n"
            "Install provider dependencies:\n"
            "  pip install se-principles-mcp[anthropic]  # or [openai] or [google] or [all]"
        )

    if name not in _PROVIDER_REGISTRY:
        available = ", ".join(sorted(_PROVIDER_REGISTRY.keys()))
        raise ValueError(
            f"Unknown provider '{name}'. Available providers: {available}"
        )

    # Step 2: Lazy-import and instantiate the provider
    module_path, class_name = _PROVIDER_REGISTRY[name]

    try:
        import importlib
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import provider '{name}': {e}\n"
            f"Install with: pip install se-principles-mcp[{name}]"
        ) from e

    provider: LLMProvider = provider_class(model=model, api_key=api_key)

    # Log provider info to stderr (doesn't interfere with MCP stdio)
    sys.stderr.write(
        f"🔧 SE Principles MCP — Using {provider.provider_name} "
        f"({provider.model_name})\n"
    )

    return provider


def _auto_detect_provider() -> str | None:
    """Auto-detect provider from available API keys.

    Checks keys in priority order: Anthropic → OpenAI → Google.
    Returns the first provider whose API key is set and non-empty.
    """
    for provider_name, env_var in _API_KEY_MAP.items():
        if os.environ.get(env_var, "").strip():
            return provider_name
    return None
