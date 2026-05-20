"""
Tool: review_naming
====================
Audit all identifiers against Clean Code naming rules by Robert C. Martin.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.naming import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    conventions: str = "auto-detect",
) -> str:
    """Build the user message for the LLM."""
    return (
        f"Language: {language}\n"
        f"Naming convention: {conventions}\n"
        f"```{language}\n{code}\n```"
    )


async def run(
    code: str,
    language: str,
    conventions: str = "auto-detect",
    *,
    llm: LLMProvider,
) -> str:
    """Audit code naming against Clean Code rules.

    Args:
        code: Code to review naming in.
        language: Programming language.
        conventions: Naming style convention (camelCase, snake_case,
            PascalCase, or 'auto-detect').
        llm: The LLM provider to use for analysis.

    Returns:
        Naming audit with before/after table and revised code.
    """
    user_message = _build_user_message(code, language, conventions)
    return await llm.generate(SYSTEM_PROMPT, user_message)
