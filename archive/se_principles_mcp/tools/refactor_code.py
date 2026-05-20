"""
Tool: refactor_code
===================
Refactor code to comply with specified SE principles while preserving
all existing functionality.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.refactor import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    principles: list[str] | None = None,
    context: str = "",
) -> str:
    """Build the user message for the LLM."""
    principle_list = (
        "all relevant principles"
        if not principles or "all" in principles
        else ", ".join(principles)
    )

    parts = [
        f"Language: {language}",
        f"Principles to apply: {principle_list}",
    ]
    if context:
        parts.append(f"Context: {context}")
    parts.append(f"```{language}\n{code}\n```")
    return "\n".join(parts)


async def run(
    code: str,
    language: str,
    principles: list[str] | None = None,
    context: str = "",
    *,
    llm: LLMProvider,
) -> str:
    """Refactor code to comply with specified SE principles.

    Args:
        code: Code to refactor.
        language: Programming language.
        principles: Principles to apply (SOLID, DRY, KISS, YAGNI, CleanCode,
            LoD, SoC, DesignPatterns). Pass None or ['all'] for everything.
        context: Optional description of what the code does.
        llm: The LLM provider to use for refactoring.

    Returns:
        Complete refactored code with a change log and metrics comparison.
    """
    user_message = _build_user_message(code, language, principles, context)
    return await llm.generate(SYSTEM_PROMPT, user_message)
