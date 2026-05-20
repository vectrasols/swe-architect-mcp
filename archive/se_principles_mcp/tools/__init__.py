"""
MCP Tool implementations for SE Principles analysis.

Each tool is a standalone async function that accepts typed parameters
and an LLM provider, following the Single Responsibility Principle.
"""

__all__ = [
    # Original 10 tools
    "analyze_principles",
    "detect_code_smells",
    "suggest_design_pattern",
    "refactor_code",
    "generate_boilerplate",
    "explain_principle",
    "review_naming",
    "check_solid",
    "architecture_review",
    "complexity_analysis",
    # Phase 2: Deep book coverage tools
    "check_error_handling",
    "check_testing_principles",
    "pragmatic_review",
    "check_concurrency",
]
