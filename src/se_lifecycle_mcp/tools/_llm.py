"""LLM helper functions for lifecycle tools."""

from __future__ import annotations

from se_lifecycle_mcp.llm.base import LLMProvider


async def generate_with_fallback(
    *,
    llm: LLMProvider | None,
    system_prompt: str,
    user_message: str,
    fallback: str,
) -> str:
    """Generate with an LLM when available, otherwise return a fallback."""
    if llm is None:
        return fallback

    try:
        text = await llm.generate(system_prompt, user_message)
    except Exception as exc:  # pragma: no cover - provider/runtime specific
        return (
            f"{fallback}\n\n"
            "## Provider Warning\n"
            f"LLM generation failed, so a deterministic fallback was used: {exc}"
        )

    return text.strip() or fallback


def strip_mermaid_fence(text: str) -> str:
    """Remove Markdown fences from model output when present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned
