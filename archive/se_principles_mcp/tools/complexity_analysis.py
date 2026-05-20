"""
Tool: complexity_analysis
==========================
Measure cyclomatic complexity, cognitive complexity, nesting depth,
and function/class size metrics with decomposition advice.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.complexity import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    threshold: int = 10,
) -> str:
    """Build the user message for the LLM."""
    return (
        f"Language: {language}\n"
        f"Complexity threshold: {threshold} (flag functions above this CC)\n"
        f"```{language}\n{code}\n```"
    )


async def run(
    code: str,
    language: str,
    threshold: int = 10,
    *,
    llm: LLMProvider,
) -> str:
    """Analyze code complexity with decomposition strategies.

    Args:
        code: Code to analyze for complexity.
        language: Programming language.
        threshold: Cyclomatic complexity threshold above which a function
            is flagged. Default: 10.
        llm: The LLM provider to use for analysis.

    Returns:
        Complexity report with metrics table, decomposition strategies,
        and a complexity reduction roadmap.
    """
    user_message = _build_user_message(code, language, threshold)
    return await llm.generate(SYSTEM_PROMPT, user_message)
