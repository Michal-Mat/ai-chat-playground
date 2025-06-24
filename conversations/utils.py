"""
Utility functions for the conversations module.

This module provides convenience functions for creating and managing
conversation instances.
"""

from conversations.manager import ConversationManager
from conversations.models import ChatSettings
from conversations.personas.personas import PERSONAS
from conversations.types import Persona


def create_conversation_manager(
    client,
    model: str = "gpt-3.5-turbo",
    system_message: str | None = None,
    title: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    **kwargs,
) -> ConversationManager:
    """
    Convenience function to create a ConversationManager with common settings.

    Args:
        client: OpenAI client instance
        model: OpenAI model to use
        system_message: Optional system message
        title: Optional conversation title
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
        **kwargs: Additional ChatSettings parameters

    Returns:
        ConversationManager instance
    """
    settings = ChatSettings(
        model=model, temperature=temperature, max_tokens=max_tokens, **kwargs
    )

    return ConversationManager(
        client=client,
        system_message=system_message,
        title=title,
        settings=settings,
    )


def create_persona_manager(
    client,
    persona: str | Persona,
    model: str = "gpt-3.5-turbo",
    **kwargs,
) -> ConversationManager:
    """
    Create a ConversationManager with predefined persona.

    Args:
        client: OpenAI client instance
        persona: Persona type ('creative', 'technical', 'teacher', 'assistant')
        model: OpenAI model to use
        **kwargs: Additional parameters

    Returns:
        ConversationManager instance with persona system message
    """
    personas = PERSONAS

    # Convert string input to Persona enum if needed
    if isinstance(persona, str):
        try:
            persona = Persona(persona)
        except ValueError as exc:
            available = ", ".join(p.value for p in Persona)
            raise ValueError(
                f"Unknown persona '{persona}'. Available: {available}"
            ) from exc

    if persona not in personas:
        available = ", ".join(p.value for p in personas.keys())
        raise ValueError(
            f"Unknown persona '{persona}'. Available: {available}"
        )

    persona_config = personas[persona]

    return create_conversation_manager(
        client=client,
        model=model,
        system_message=persona_config["system_message"],
        title=persona_config["title"],
        **kwargs,
    )
