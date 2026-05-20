"""
Tool: check_error_handling
===========================
Audit error handling against Clean Code Ch.7, Code Complete Ch.8
(Defensive Programming), and Pragmatic Programmer's Pragmatic Paranoia.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.error_handling import SYSTEM_PROMPT


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
    """Audit code error handling against Clean Code and Code Complete.

    Args:
        code: The source code to audit for error handling.
        language: Programming language.
        context: Optional description of what the code does.
        llm: The LLM provider to use for analysis.

    Returns:
        A comprehensive error handling audit report with scorecard.
    """
    user_message = _build_user_message(code, language, context)
    return await llm.generate(SYSTEM_PROMPT, user_message)
