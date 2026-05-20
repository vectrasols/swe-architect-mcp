"""
Tool: check_solid
==================
Dedicated per-letter SOLID principles audit with compliance verdicts,
evidence, and refactoring guidance.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.solid_check import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    principles: list[str] | None = None,
) -> str:
    """Build the user message for the LLM."""
    scope = (
        f"Check ONLY these SOLID letters: {', '.join(principles)}"
        if principles
        else "Check all five SOLID principles."
    )
    return (
        f"Language: {language}\n"
        f"{scope}\n"
        f"```{language}\n{code}\n```"
    )


async def run(
    code: str,
    language: str,
    principles: list[str] | None = None,
    *,
    llm: LLMProvider,
) -> str:
    """Check code for SOLID principles compliance.

    Args:
        code: Code to audit for SOLID compliance.
        language: Programming language.
        principles: Specific SOLID letters to check ('S', 'O', 'L', 'I', 'D').
            Pass None to check all five.
        llm: The LLM provider to use for analysis.

    Returns:
        Per-letter SOLID audit with scorecard and refactoring guidance.
    """
    user_message = _build_user_message(code, language, principles)
    return await llm.generate(SYSTEM_PROMPT, user_message)
