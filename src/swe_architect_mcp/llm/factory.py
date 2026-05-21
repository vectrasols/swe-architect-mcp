"""LLM provider factory for the SWE Architect MCP."""

from __future__ import annotations

import os
import sys

from swe_architect_mcp.llm.base import LLMProvider


# Provider registry maps provider names to their module and class.
_PROVIDER_REGISTRY: dict[str, tuple[str, str]] = {
    "anthropic": ("swe_architect_mcp.llm.anthropic", "AnthropicProvider"),
    "openai": ("swe_architect_mcp.llm.openai", "OpenAIProvider"),
    "google": ("swe_architect_mcp.llm.google", "GoogleProvider"),
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
        2. `SWE_ARCHITECT_MCP_PROVIDER` environment variable
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
    env_provider = os.environ.get("SWE_ARCHITECT_MCP_PROVIDER", "").strip().lower()
    
    # Try to infer provider from model name if explicit provider is not given
    inferred_from_model = None
    model_to_check = (model or os.environ.get("SWE_ARCHITECT_MCP_MODEL", "")).strip().lower()
    if model_to_check:
        if "claude" in model_to_check:
            inferred_from_model = "anthropic"
        elif "gpt" in model_to_check or "o1" in model_to_check or "o3" in model_to_check:
            inferred_from_model = "openai"
        elif "gemini" in model_to_check:
            inferred_from_model = "google"

    # Try to infer provider from SWE_ARCHITECT_MCP_API_KEY if model didn't give a clue
    inferred_from_key = None
    api_key_to_check = (api_key or os.environ.get("SWE_ARCHITECT_MCP_API_KEY", "")).strip()
    if api_key_to_check and not inferred_from_model:
        if api_key_to_check.startswith("sk-ant"):
            inferred_from_key = "anthropic"
        elif api_key_to_check.startswith("sk-proj") or api_key_to_check.startswith("sk-"):
            inferred_from_key = "openai"
        elif api_key_to_check.startswith("AIza"):
            inferred_from_key = "google"

    name = (
        provider_name
        or env_provider
        or inferred_from_model
        or inferred_from_key
        or _auto_detect_provider()
    )

    if not name:
        raise ValueError(
            "No LLM provider configured. Set one of the following environment variables:\n"
            "  - ANTHROPIC_API_KEY  (for Anthropic Claude)\n"
            "  - OPENAI_API_KEY    (for OpenAI GPT)\n"
            "  - GOOGLE_API_KEY    (for Google Gemini)\n"
            "\n"
            "Or explicitly set SWE_ARCHITECT_MCP_PROVIDER=anthropic|openai|google\n"
            "\n"
            "Install provider dependencies:\n"
            "  pip install swe-architect-mcp[anthropic]  # or [openai] or [google] or [all]"
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
            f"Install with: pip install swe-architect-mcp[{name}]"
        ) from e

    api_key_to_use = api_key or os.environ.get("SWE_ARCHITECT_MCP_API_KEY")
    provider: LLMProvider = provider_class(model=model, api_key=api_key_to_use)

    # Log provider info to stderr; this does not interfere with MCP stdio.
    sys.stderr.write(
        f"SWE Architect MCP using {provider.provider_name} "
        f"({provider.model_name})\n"
    )

    return provider


def _auto_detect_provider() -> str | None:
    """Auto-detect provider from available API keys.

    Checks keys in priority order: Anthropic, OpenAI, then Google.
    Returns the first provider whose API key is set and non-empty.
    """
    for provider_name, env_var in _API_KEY_MAP.items():
        if os.environ.get(env_var, "").strip():
            return provider_name
    return None
