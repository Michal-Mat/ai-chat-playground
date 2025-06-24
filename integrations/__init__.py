"""
Integrations Package

This package provides integration layers for various AI/ML services
with proper data validation and type safety.

Available modules:
- openai: OpenAI API integration with client wrapper
- conversations: Conversation management with Pydantic models
"""

# OpenAI integration
from .openai import OpenAIClient, create_openai_client

# Import conversations at package level for convenience
try:
    from conversations import (
        ChatSettings,
        Conversation,
        ConversationManager,
        Message,
        create_conversation_manager,
        create_persona_manager,
    )

    _conversations_available = True
except ImportError:
    _conversations_available = False

__all__ = [
    # OpenAI
    "OpenAIClient",
    "create_openai_client",
]

# Add conversations to __all__ if available
if _conversations_available:
    __all__.extend(
        [
            "ConversationManager",
            "create_conversation_manager",
            "create_persona_manager",
            "Message",
            "Conversation",
            "ChatSettings",
        ]
    )
