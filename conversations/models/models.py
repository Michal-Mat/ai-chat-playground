"""
Pydantic models for conversation management.

These models provide type safety, validation, and serialization
for chat messages and conversation data.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import json
from conversations.types import Role, Persona


class Message(BaseModel):
    """
    Represents a single chat message with role-based validation.

    Supports OpenAI's message format with validation.
    """
    role: Role = Field(..., description="The role of the message sender")
    content: str = Field(
        ...,
        min_length=1,
        description="The message content"
    )
    model: Optional[str] = Field(
        default=None,
        description=(
            "Model that generated the message "
            "(assistant only)"
        ),
    )
    persona: Optional[Persona] = Field(
        default=None,
        description="Persona used for the assistant reply",
    )
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When the message was created"
    )

    @field_validator('content')
    def content_must_not_be_empty(cls, v):
        """Ensure content is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty or just whitespace')
        return v.strip()

    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI API format."""
        return {
            "role": self.role.value,
            "content": self.content
        }

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatSettings(BaseModel):
    """
    Configuration settings for chat completion requests.
    """
    model: str = Field(
        default="gpt-3.5-turbo",
        description="The OpenAI model to use"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0-2.0)"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        le=4096,
        description="Maximum tokens in response"
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    frequency_penalty: Optional[float] = Field(
        default=None,
        ge=-2.0,
        le=2.0,
        description="Frequency penalty (-2.0 to 2.0)"
    )
    presence_penalty: Optional[float] = Field(
        default=None,
        ge=-2.0,
        le=2.0,
        description="Presence penalty (-2.0 to 2.0)"
    )
    persona: Optional[Persona] = Field(
        default=None,
        description="Assistant persona to use",
    )

    @field_validator('model')
    def validate_model_name(cls, v):
        """Basic model name validation."""
        if not v or not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip()


class ConversationMetadata(BaseModel):
    """
    Metadata for a conversation session.
    """
    id: str = Field(..., description="Unique conversation identifier")
    title: Optional[str] = Field(
        default=None,
        description="Optional conversation title"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="When the conversation was last updated"
    )
    message_count: int = Field(
        default=0,
        ge=0,
        description="Total number of messages"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Optional tags for categorization"
    )


class Conversation(BaseModel):
    """
    Complete conversation with messages, settings, and metadata.
    """
    metadata: ConversationMetadata
    settings: ChatSettings
    messages: List[Message] = Field(
        default_factory=list,
        description="List of conversation messages"
    )

    def add_message(
        self,
        role: Role,
        content: str,
        model: Optional[str] = None,
        persona: Optional[Persona] = None,
    ) -> Message:
        """Add a message to the conversation."""
        message = Message(
            role=role,
            content=content,
            model=model,
            persona=persona,
        )
        self.messages.append(message)
        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now()
        return message

    def get_openai_messages(self) -> List[Dict[str, str]]:
        """Get messages in OpenAI API format."""
        return [msg.to_openai_format() for msg in self.messages]

    def get_system_message(self) -> Optional[Message]:
        """Get the system message if it exists."""
        for msg in self.messages:
            if msg.role == Role.SYSTEM:
                return msg
        return None

    def get_conversation_history(self, include_system: bool = True) -> List[Message]:
        """Get conversation history, optionally excluding system messages."""
        if include_system:
            return self.messages.copy()
        return [msg for msg in self.messages if msg.role != Role.SYSTEM]

    def clear_messages(self, keep_system: bool = True):
        """Clear all messages, optionally keeping system message."""
        if keep_system:
            system_messages = [
                msg for msg in self.messages if msg.role == Role.SYSTEM
            ]
            self.messages = system_messages
        else:
            self.messages = []

        self.metadata.message_count = len(self.messages)
        self.metadata.updated_at = datetime.now()

    def export_to_dict(self) -> Dict[str, Any]:
        """Export conversation to dictionary format."""
        return self.dict()

    def export_to_json(self, filepath: Optional[str] = None) -> str:
        """Export conversation to JSON format."""
        data = self.export_to_dict()
        json_str = json.dumps(data, indent=2, default=str)

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)

        return json_str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Conversation':
        """Create conversation from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_json_file(cls, filepath: str) -> 'Conversation':
        """Load conversation from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }