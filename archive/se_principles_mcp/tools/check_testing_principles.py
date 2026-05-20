"""
Tool: check_testing_principles
================================
Audit test code (or production code testability) against FIRST principles
(Clean Code Ch.9), developer testing (Code Complete Ch.22), and
Pragmatic Programmer's ruthless testing philosophy.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.testing_principles import SYSTEM_PROMPT


def _build_user_message(
    code: str,
    language: str,
    test_code: str = "",
    context: str = "",
) -> str:
    """Build the user message for the LLM."""
    parts = [f"Language: {language}"]
    if context:
        parts.append(f"Context: {context}")

    parts.append(f"### Production Code\n```{language}\n{code}\n```")

    if test_code:
        parts.append(f"### Test Code\n```{language}\n{test_code}\n```")
    else:
        parts.append("### Test Code\nNo test code provided — analyze production code testability and suggest tests.")

    return "\n".join(parts)


async def run(
    code: str,
    language: str,
    test_code: str = "",
    context: str = "",
    *,
    llm: LLMProvider,
) -> str:
    """Audit testing practices against FIRST principles and developer testing.

    Args:
        code: The production source code to analyze testability for.
        language: Programming language.
        test_code: Optional existing test code to audit.
        context: Optional description of what the code does.
        llm: The LLM provider to use for analysis.

    Returns:
        A comprehensive testing audit with FIRST compliance, test smells,
        missing test cases, and testability analysis.
    """
    user_message = _build_user_message(code, language, test_code, context)
    return await llm.generate(SYSTEM_PROMPT, user_message)
