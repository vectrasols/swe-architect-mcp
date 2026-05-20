"""
Tool: suggest_design_pattern
=============================
Recommend the most suitable design pattern(s) from the GoF catalog
plus modern patterns for a given problem.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.suggest_pattern import SYSTEM_PROMPT


def _build_user_message(problem: str, language: str, constraints: str = "") -> str:
    """Build the user message for the LLM."""
    parts = [f"Language: {language}"]
    if constraints:
        parts.append(f"Constraints: {constraints}")
    parts.append(f"Problem / Code:\n{problem}")
    return "\n".join(parts)


async def run(
    problem: str,
    language: str,
    constraints: str = "",
    *,
    llm: LLMProvider,
) -> str:
    """Suggest the best design pattern(s) for a given problem.

    Args:
        problem: Problem description or existing code needing a pattern.
        language: Target programming language for examples.
        constraints: Optional constraints or patterns to avoid.
        llm: The LLM provider to use for analysis.

    Returns:
        Pattern recommendation with implementation example and trade-offs.
    """
    user_message = _build_user_message(problem, language, constraints)
    return await llm.generate(SYSTEM_PROMPT, user_message)
