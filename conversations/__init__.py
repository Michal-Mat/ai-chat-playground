"""
Conversations Module

This module provides conversation management functionality with data validation
using Pydantic models for type safety and validation.
"""

from .manager import ConversationManager
from .models import ChatSettings, Conversation, Message
from .utils import create_conversation_manager, create_persona_manager

__all__ = [
    "Message",
    "Conversation",
    "ChatSettings",
    "ConversationManager",
    "create_conversation_manager",
    "create_persona_manager",
]
