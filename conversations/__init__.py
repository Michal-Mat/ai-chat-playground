"""
Conversations Module

This module provides conversation management functionality with data validation
using Pydantic models for type safety and validation.
"""

from .models import Message, Conversation, ChatSettings
from .manager import ConversationManager
from .utils import create_conversation_manager

__all__ = [
    "Message",
    "Conversation",
    "ChatSettings",
    "ConversationManager",
    "create_conversation_manager"
]