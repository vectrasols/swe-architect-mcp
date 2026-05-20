"""
Tool: generate_boilerplate
===========================
Generate production-ready, principle-compliant boilerplate for common
patterns and architectures.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.boilerplate import SYSTEM_PROMPT


def _build_user_message(
    pattern: str,
    language: str,
    domain: str = "",
    requirements: str = "",
) -> str:
    """Build the user message for the LLM."""
    parts = [
        f"Pattern: {pattern}",
        f"Language: {language}",
    ]
    if domain:
        parts.append(f"Domain: {domain}")
    if requirements:
        parts.append(f"Requirements: {requirements}")
    return "\n".join(parts)


async def run(
    pattern: str,
    language: str,
    domain: str = "",
    requirements: str = "",
    *,
    llm: LLMProvider,
) -> str:
    """Generate principle-compliant boilerplate code.

    Args:
        pattern: Pattern or architecture to generate (e.g., 'Repository Pattern',
            'Clean Architecture', 'CQRS').
        language: Target programming language.
        domain: Optional business domain for meaningful naming.
        requirements: Optional specific requirements or features.
        llm: The LLM provider to use for generation.

    Returns:
        Complete boilerplate with file structure, code, and extension guide.
    """
    user_message = _build_user_message(pattern, language, domain, requirements)
    return await llm.generate(SYSTEM_PROMPT, user_message)
