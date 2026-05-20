"""
Tool: detect_code_smells
========================
Identify code smells from Fowler's catalog and suggest matching
refactoring techniques for each.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.detect_smells import SYSTEM_PROMPT


def _build_user_message(code: str, language: str) -> str:
    """Build the user message for the LLM."""
    return f"Language: {language}\n```{language}\n{code}\n```"


async def run(
    code: str,
    language: str,
    *,
    llm: LLMProvider,
) -> str:
    """Detect code smells and suggest refactoring techniques.

    Args:
        code: The source code to smell-check.
        language: Programming language.
        llm: The LLM provider to use for analysis.

    Returns:
        A structured code smell report with refactoring suggestions.
    """
    user_message = _build_user_message(code, language)
    return await llm.generate(SYSTEM_PROMPT, user_message)
