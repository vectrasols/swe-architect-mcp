"""System prompts for SE Principles analysis tools."""

from se_principles_mcp.prompts.analyze_principles import SYSTEM_PROMPT as ANALYZE_PRINCIPLES
from se_principles_mcp.prompts.detect_smells import SYSTEM_PROMPT as DETECT_SMELLS
from se_principles_mcp.prompts.suggest_pattern import SYSTEM_PROMPT as SUGGEST_PATTERN
from se_principles_mcp.prompts.refactor import SYSTEM_PROMPT as REFACTOR
from se_principles_mcp.prompts.boilerplate import SYSTEM_PROMPT as BOILERPLATE
from se_principles_mcp.prompts.explain import SYSTEM_PROMPT as EXPLAIN
from se_principles_mcp.prompts.naming import SYSTEM_PROMPT as NAMING
from se_principles_mcp.prompts.solid_check import SYSTEM_PROMPT as SOLID_CHECK
from se_principles_mcp.prompts.architecture import SYSTEM_PROMPT as ARCHITECTURE
from se_principles_mcp.prompts.complexity import SYSTEM_PROMPT as COMPLEXITY
from se_principles_mcp.prompts.error_handling import SYSTEM_PROMPT as ERROR_HANDLING
from se_principles_mcp.prompts.testing_principles import SYSTEM_PROMPT as TESTING_PRINCIPLES
from se_principles_mcp.prompts.pragmatic_review import SYSTEM_PROMPT as PRAGMATIC_REVIEW
from se_principles_mcp.prompts.concurrency import SYSTEM_PROMPT as CONCURRENCY

__all__ = [
    "ANALYZE_PRINCIPLES",
    "DETECT_SMELLS",
    "SUGGEST_PATTERN",
    "REFACTOR",
    "BOILERPLATE",
    "EXPLAIN",
    "NAMING",
    "SOLID_CHECK",
    "ARCHITECTURE",
    "COMPLEXITY",
    "ERROR_HANDLING",
    "TESTING_PRINCIPLES",
    "PRAGMATIC_REVIEW",
    "CONCURRENCY",
]
