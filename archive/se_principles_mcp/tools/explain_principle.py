"""
Tool: explain_principle
========================
In-depth explanation of any SE principle with real-world analogies,
good vs bad code examples, and "when NOT to apply" guidance.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.explain import SYSTEM_PROMPT


def _build_user_message(
    principle: str,
    language: str = "Python",
    experience_level: str = "mid",
) -> str:
    """Build the user message for the LLM."""
    return (
        f"Principle: {principle}\n"
        f"Code examples language: {language}\n"
        f"Experience level: {experience_level}"
    )


async def run(
    principle: str,
    language: str = "Python",
    experience_level: str = "mid",
    *,
    llm: LLMProvider,
) -> str:
    """Explain an SE principle in depth with examples.

    Args:
        principle: The principle name (e.g., 'Single Responsibility', 'DRY',
            'KISS', 'Law of Demeter', 'Composition over Inheritance').
        language: Preferred language for code examples.
        experience_level: Adjusts depth — 'junior', 'mid', or 'senior'.
        llm: The LLM provider to use for explanation.

    Returns:
        A comprehensive principle explanation with examples and caveats.
    """
    user_message = _build_user_message(principle, language, experience_level)
    return await llm.generate(SYSTEM_PROMPT, user_message)
