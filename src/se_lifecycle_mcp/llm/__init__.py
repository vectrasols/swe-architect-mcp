"""
LLM Provider Abstraction Layer
===============================
Strategy + Factory pattern for multi-provider LLM support.
Follows Dependency Inversion Principle: tools depend on the abstract
LLMProvider interface, not on concrete SDK implementations.
"""

from se_lifecycle_mcp.llm.base import LLMProvider
from se_lifecycle_mcp.llm.factory import create_provider

__all__ = ["LLMProvider", "create_provider"]
