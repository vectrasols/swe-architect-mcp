"""
Tool: check_concurrency
========================
Audit concurrent/async code against Clean Code Ch.13, common concurrency
bugs (race conditions, deadlocks), async/await anti-patterns, and
data consistency principles from Designing Data-Intensive Applications.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.concurrency import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    concurrency_model: str = "auto-detect",
    context: str = "",
) -> str:
    """Build the user message for the LLM."""
    parts = [
        f"Language: {language}",
        f"Concurrency model: {concurrency_model}",
    ]
    if context:
        parts.append(f"Context: {context}")
    parts.append(f"```{language}\n{code}\n```")
    return "\n".join(parts)


async def run(
    code: str,
    language: str,
    concurrency_model: str = "auto-detect",
    context: str = "",
    *,
    llm: LLMProvider,
) -> str:
    """Audit code for concurrency safety and correctness.

    Args:
        code: The source code to audit for concurrency issues.
        language: Programming language.
        concurrency_model: Concurrency model used (threads, async-await,
            multiprocessing, actors, or 'auto-detect').
        context: Optional description of what the code does.
        llm: The LLM provider to use for analysis.

    Returns:
        A concurrency audit report with shared state map, issue details,
        and a concurrency scorecard.
    """
    user_message = _build_user_message(code, language, concurrency_model, context)
    return await llm.generate(SYSTEM_PROMPT, user_message)
