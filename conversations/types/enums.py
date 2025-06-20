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
