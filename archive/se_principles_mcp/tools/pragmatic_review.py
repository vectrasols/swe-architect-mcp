"""
Tool: pragmatic_review
=======================
Dedicated audit against The Pragmatic Programmer by Andrew Hunt & David Thomas.
Covers DRY (all 4 types), Orthogonality, Design by Contract, Broken Windows,
Reversibility, Decoupling, and Programming by Coincidence.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.pragmatic_review import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    context: str = "",
    focus_areas: list[str] | None = None,
) -> str:
    """Build the user message for the LLM."""
    parts = [f"Language: {language}"]
    if context:
        parts.append(f"Context: {context}")
    if focus_areas:
        parts.append(f"Focus areas: {', '.join(focus_areas)}")
    parts.append(f"```{language}\n{code}\n```")
    return "\n".join(parts)


async def run(
    code: str,
    language: str,
    context: str = "",
    focus_areas: list[str] | None = None,
    *,
    llm: LLMProvider,
) -> str:
    """Run a Pragmatic Programmer audit on the provided code.

    Args:
        code: The source code to audit.
        language: Programming language.
        context: Optional description of what the code does.
        focus_areas: Optional list of specific areas to focus on
            (e.g., ['DRY', 'Orthogonality', 'Design by Contract']).
        llm: The LLM provider to use for analysis.

    Returns:
        A Pragmatic Programmer audit report with orthogonality map,
        reversibility assessment, broken windows list, and scorecard.
    """
    user_message = _build_user_message(code, language, context, focus_areas)
    return await llm.generate(SYSTEM_PROMPT, user_message)
