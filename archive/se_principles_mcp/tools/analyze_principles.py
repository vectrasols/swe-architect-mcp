"""
Tool: analyze_principles
========================
Comprehensive analysis of code against ALL major SE principles:
SOLID, DRY, KISS, YAGNI, Clean Code, Law of Demeter, and Separation of Concerns.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.analyze_principles import SYSTEM_PROMPT


def _build_user_message(code: str, language: str, context: str = "") -> str:
    """Build the user message for the LLM."""
    parts = [f"Language: {language}"]
    if context:
        parts.append(f"Context: {context}")
    parts.append(f"```{language}\n{code}\n```")
    return "\n".join(parts)


async def run(
    code: str,
    language: str,
    context: str = "",
    *,
    llm: LLMProvider,
) -> str:
    """Run a comprehensive SE principles analysis on the provided code.

    Args:
        code: The source code to analyze.
        language: Programming language (e.g., python, typescript, java).
        context: Optional description of what the code does.
        llm: The LLM provider to use for analysis.

    Returns:
        A structured analysis report as a formatted string.
    """
    user_message = _build_user_message(code, language, context)
    return await llm.generate(SYSTEM_PROMPT, user_message)
