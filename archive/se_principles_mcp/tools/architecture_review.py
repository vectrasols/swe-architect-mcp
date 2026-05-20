"""
Tool: architecture_review
==========================
Review system architecture against SE best practices: layering,
coupling/cohesion, dependency direction, testability, and scalability.
"""

from se_principles_mcp.llm.base import LLMProvider
from se_principles_mcp.prompts.architecture import SYSTEM_PROMPT


def _build_user_message(
    description: str,
    architecture_type: str = "unspecified",
    scale: str = "unspecified",
) -> str:
    """Build the user message for the LLM."""
    return (
        f"Architecture Style: {architecture_type}\n"
        f"Scale: {scale}\n"
        f"Description:\n{description}"
    )


async def run(
    description: str,
    architecture_type: str = "unspecified",
    scale: str = "unspecified",
    *,
    llm: LLMProvider,
) -> str:
    """Review a system architecture against SE best practices.

    Args:
        description: Architecture description, component list, or design document.
        architecture_type: Architecture style (e.g., monolith, microservices,
            hexagonal, event-driven, serverless).
        scale: Expected scale (e.g., 'startup MVP', '10M users/day', 'enterprise').
        llm: The LLM provider to use for analysis.

    Returns:
        Architecture review with strengths, concerns, anti-patterns, and scorecard.
    """
    user_message = _build_user_message(description, architecture_type, scale)
    return await llm.generate(SYSTEM_PROMPT, user_message)
