# noqa: D100

from enum import Enum


class Role(str, Enum):
    """Enumeration of sender roles in a chat message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# noqa: D101

class Persona(str, Enum):
    """Enumeration of predefined chat personas."""

    CREATIVE = "creative"
    TECHNICAL = "technical"
    TEACHER = "teacher"
    ASSISTANT = "assistant"
    PERSONAL_ASSISTANT = "personal_assistant"


class ChatModel(str, Enum):
    """Enumeration of supported OpenAI chat/completion models."""

    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT_4O_MINI = "gpt-4o-mini"  # 128k context, faster
    GPT_4O_128K = "gpt-4o-128k"
    GPT_4O = "gpt-4o"
