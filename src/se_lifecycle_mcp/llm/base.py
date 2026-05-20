"""
Abstract base class for LLM providers.

Any LLM provider (Anthropic, OpenAI, Google, local models, etc.) must
implement this interface. Lifecycle tools depend on this abstraction, never on
concrete SDK implementations.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for LLM providers.

    Implementations must provide a `generate` method that accepts a system
    prompt and user message, returning the model's text response.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of the provider (e.g., 'Anthropic', 'OpenAI')."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model identifier being used (e.g., 'claude-sonnet-4-20250514')."""
        ...

    @abstractmethod
    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a text response from the LLM.

        Args:
            system_prompt: The system-level instruction defining the AI's role
                and response format.
            user_message: The user's input containing code, questions, or
                descriptions to analyze.

        Returns:
            The model's text response as a string.

        Raises:
            Exception: If the API call fails (network error, auth error, etc.).
        """
        ...
