"""
Conversation Manager using Pydantic models for type safety and validation.

This module provides the ConversationManager class that handles chat sessions
with OpenAI models while maintaining conversation history and state.
"""

import logging
from typing import Optional, List
from datetime import datetime
import uuid

from conversations.models import (
    Message,
    Conversation,
    ChatSettings,
    ConversationMetadata,
)
from conversations.types import Role
from persistence.mongo_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversations with OpenAI models using validated Pydantic models.

    This class provides a high-level interface for chat interactions while
    maintaining conversation history, settings, and metadata.
    """

    def __init__(
        self,
        client,
        model: str = "gpt-3.5-turbo",
        system_message: Optional[str] = None,
        conversation_id: Optional[str] = None,
        title: Optional[str] = None,
        settings: Optional[ChatSettings] = None,
        repository: Optional[ConversationRepository] = None,
    ):
        """
        Initialize a conversation manager.

        Args:
            client: OpenAI client instance
            model: OpenAI model to use
            system_message: Optional system message to set behavior
            conversation_id: Optional custom conversation ID
            title: Optional conversation title
            settings: Optional ChatSettings instance
            repository: Optional ConversationRepository instance
        """
        self.client = client

        # Store repository (defaults to a new Mongo-backed repository)
        self.repository: ConversationRepository = repository or ConversationRepository()

        # Create conversation metadata
        metadata = ConversationMetadata(
            id=conversation_id or str(uuid.uuid4()),
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Create chat settings
        if settings is None:
            settings = ChatSettings(model=model)

        # Initialize conversation
        self.conversation = Conversation(metadata=metadata, settings=settings)

        # Add system message if provided
        if system_message:
            self.add_system_message(system_message)

        logger.info(f"ConversationManager initialized: {self.conversation.metadata.id}")

    def add_system_message(self, content: str) -> Message:
        """Add a system message to set AI behavior."""
        return self.conversation.add_message(Role.SYSTEM, content)

    def add_user_message(self, content: str) -> Message:
        """Add a user message to the conversation."""
        return self.conversation.add_message(Role.USER, content)

    def add_assistant_message(
        self, content: str, token_count: Optional[int] = None
    ) -> Message:
        """Add an assistant message and record the model used."""
        model_name = self.conversation.settings.model
        persona_val = self.conversation.settings.persona
        return self.conversation.add_message(
            Role.ASSISTANT,
            content,
            model=model_name,
            persona=persona_val,
            token_count=token_count,
        )

    async def get_ai_response_async(
        self, settings_override: Optional[ChatSettings] = None
    ) -> str:
        """
        Get AI response asynchronously using current conversation state.

        Args:
            settings_override: Optional settings to override defaults

        Returns:
            AI response content
        """
        settings = settings_override or self.conversation.settings

        try:
            response = await self.client.async_chat_completion(
                messages=self.conversation.get_openai_messages(),
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                top_p=settings.top_p,
                frequency_penalty=settings.frequency_penalty,
                presence_penalty=settings.presence_penalty,
            )

            ai_content = response.choices[0].message.content
            self.add_assistant_message(ai_content)

            logger.info(
                f"AI response received for conversation {self.conversation.metadata.id}"
            )
            return ai_content

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            logger.error(error_msg)
            raise

    def get_ai_response(self, settings_override: Optional[ChatSettings] = None) -> str:
        """
        Get AI response synchronously using current conversation state.

        Args:
            settings_override: Optional settings to override defaults

        Returns:
            AI response content
        """
        settings = settings_override or self.conversation.settings

        try:
            response = self.client.chat_completion(
                messages=self.conversation.get_openai_messages(),
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                top_p=settings.top_p,
                frequency_penalty=settings.frequency_penalty,
                presence_penalty=settings.presence_penalty,
            )

            ai_content = response.choices[0].message.content
            # Extract token count from response
            token_count = (
                getattr(response.usage, "completion_tokens", None)
                if hasattr(response, "usage")
                else None
            )
            self.add_assistant_message(ai_content, token_count)

            # Auto-save if conversation has content
            self._auto_save()

            logger.info(
                f"AI response received for conversation {self.conversation.metadata.id}"
            )
            return ai_content

        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            logger.error(error_msg)
            raise

    def chat(
        self, user_message: str, settings_override: Optional[ChatSettings] = None
    ) -> str:
        """Send a user message and get an AI response.

        If the *reasoning* flag is enabled in the active ``ChatSettings`` (or
        the provided ``settings_override``) the manager will invoke the
        multi-step reasoning flow. Otherwise it will default to a single call
        to the model.
        """

        settings = settings_override or self.conversation.settings

        # If reasoning toggle is active, run the advanced flow.
        if getattr(settings, "reasoning", False):
            return self.chat_with_reasoning(user_message, settings_override)

        # Otherwise fall back to the normal single-shot flow.
        self.add_user_message(user_message)
        return self.get_ai_response(settings_override)

    async def chat_async(
        self, user_message: str, settings_override: Optional[ChatSettings] = None
    ) -> str:
        """
        Send a user message and get AI response asynchronously.

        Args:
            user_message: The user's message
            settings_override: Optional settings to override defaults

        Returns:
            AI response content
        """
        self.add_user_message(user_message)
        return await self.get_ai_response_async(settings_override)

    def update_settings(self, **kwargs) -> ChatSettings:
        """
        Update chat settings.

        Args:
            **kwargs: Settings to update (model, temperature, etc.)

        Returns:
            Updated ChatSettings instance
        """
        # Check if persona is being updated
        persona_changed = 'persona' in kwargs
        old_persona = self.conversation.settings.persona if persona_changed else None
        new_persona = kwargs.get('persona') if persona_changed else None

        current_settings = self.conversation.settings.dict()
        current_settings.update(kwargs)

        new_settings = ChatSettings(**current_settings)
        self.conversation.settings = new_settings
        self.conversation.metadata.updated_at = datetime.now()

        # Auto-update system prompt when persona changes
        if persona_changed and old_persona != new_persona:
            self._update_system_prompt_for_persona(new_persona)

        logger.info(
            f"Settings updated for conversation {self.conversation.metadata.id}"
        )
        return new_settings

    def get_messages(self, include_system: bool = True) -> List[Message]:
        """Get conversation messages."""
        return self.conversation.get_conversation_history(include_system)

    def get_message_count(self) -> int:
        """Get total message count."""
        return len(self.conversation.messages)

    def show_conversation(self) -> None:
        """Display the full conversation history in a formatted way."""
        print(
            f"📜 Conversation: {self.conversation.metadata.title or self.conversation.metadata.id}"
        )
        print(
            f"🕒 Created: {self.conversation.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"📊 Messages: {self.conversation.metadata.message_count}")
        print(f"🤖 Model: {self.conversation.settings.model}")
        print("=" * 60)

        for message in self.conversation.messages:
            if message.role == Role.SYSTEM:
                print(f"🎯 System: {message.content}")
            elif message.role == Role.USER:
                print(f"👤 You: {message.content}")
            elif message.role == Role.ASSISTANT:
                print(f"🤖 AI: {message.content}")

            # Show timestamp for debugging if needed
            if hasattr(message, "timestamp") and message.timestamp:
                timestamp_str = message.timestamp.strftime("%H:%M:%S")
                print(f"   ⏰ {timestamp_str}")
            print()

    def clear_conversation(self, keep_system: bool = True) -> None:
        """
        Clear conversation history.

        Args:
            keep_system: Whether to keep system messages
        """
        self.conversation.clear_messages(keep_system)
        logger.info(f"Conversation cleared: {self.conversation.metadata.id}")
        print("🧹 Conversation cleared!")

    def export_conversation(self, filepath: Optional[str] = None) -> str:
        """
        Export conversation to JSON file.

        Args:
            filepath: Optional file path. If None, auto-generates filename.

        Returns:
            JSON string of the conversation
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title_part = self.conversation.metadata.title or "conversation"
            title_part = "".join(
                c for c in title_part if c.isalnum() or c in (" ", "-", "_")
            ).strip()
            title_part = title_part.replace(" ", "_").lower()
            filepath = f"{title_part}_{timestamp}.json"

        json_str = self.conversation.export_to_json(filepath)
        logger.info(f"Conversation exported to {filepath}")
        print(f"💾 Conversation exported to {filepath}")
        return json_str

    def set_title(self, title: str) -> None:
        """Set conversation title."""
        self.conversation.metadata.title = title
        self.conversation.metadata.updated_at = datetime.now()
        logger.info(
            f"Title set for conversation {self.conversation.metadata.id}: {title}"
        )

    def add_tags(self, *tags: str) -> None:
        """Add tags to conversation."""
        for tag in tags:
            if tag not in self.conversation.metadata.tags:
                self.conversation.metadata.tags.append(tag)

        self.conversation.metadata.updated_at = datetime.now()
        logger.info(
            f"Tags added to conversation {self.conversation.metadata.id}: {tags}"
        )

    def get_conversation_data(self) -> Conversation:
        """Get the underlying Conversation model."""
        return self.conversation

    @classmethod
    def from_conversation(
        cls, client, conversation: Conversation
    ) -> "ConversationManager":
        """
        Create ConversationManager from existing Conversation model.

        Args:
            client: OpenAI client instance
            conversation: Existing Conversation instance

        Returns:
            ConversationManager instance
        """
        manager = cls.__new__(cls)
        manager.client = client
        manager.conversation = conversation
        logger.info(
            f"ConversationManager loaded from conversation: {conversation.metadata.id}"
        )
        return manager

    @classmethod
    def from_json_file(cls, client, filepath: str) -> "ConversationManager":
        """
        Load ConversationManager from JSON file.

        Args:
            client: OpenAI client instance
            filepath: Path to JSON file

        Returns:
            ConversationManager instance
        """
        conversation = Conversation.from_json_file(filepath)
        return cls.from_conversation(client, conversation)

    def save_to_repository(self) -> None:
        """Persist the current conversation state to the configured repository."""
        self.repository.save(self.conversation)
        logger.info(f"Conversation {self.conversation.metadata.id} saved to repository")

    def _auto_save(self) -> None:
        """Auto-save conversation if it has content (not empty)."""
        # Only save if conversation has user/assistant messages (not just system)
        non_system_messages = [
            msg for msg in self.conversation.messages if msg.role != Role.SYSTEM
        ]
        if non_system_messages:
            self.save_to_repository()
        else:
            logger.debug(
                f"Skipping auto-save for empty conversation {self.conversation.metadata.id}"
            )

    def is_empty(self) -> bool:
        """Check if conversation is empty (no user/assistant messages)."""
        return (
            len([msg for msg in self.conversation.messages if msg.role != Role.SYSTEM])
            == 0
        )

    @classmethod
    def load_from_repository(
        cls,
        client,
        conversation_id: str,
        repository: Optional[ConversationRepository] = None,
    ) -> "ConversationManager":
        """Retrieve a conversation by ID from the repository and return a manager instance."""
        repo = repository or ConversationRepository()
        conversation = repo.get(conversation_id)
        if conversation is None:
            raise ValueError(
                f"Conversation with id {conversation_id} not found in repository"
            )
        manager = cls.from_conversation(client, conversation)
        manager.repository = repo  # type: ignore[attr-defined]
        return manager

    # ------------------------------------------------------------------
    # System prompt utilities
    # ------------------------------------------------------------------

    def _update_system_prompt_for_persona(self, persona) -> None:
        """
        Update system prompt based on persona selection.

        Args:
            persona: The persona to set (or None to clear)
        """
        from conversations.personas.personas import PERSONAS

        if persona is None:
            # Clear persona-specific system prompt, but don't remove custom ones
            sys_msg = self.conversation.get_system_message()
            if sys_msg and any(
                sys_msg.content == config["system_message"]
                for config in PERSONAS.values()
            ):
                # This is a persona system message, remove it
                self.conversation.messages = [
                    msg for msg in self.conversation.messages
                    if msg.role != Role.SYSTEM or msg != sys_msg
                ]
                logger.info(f"Cleared persona system prompt for conversation {self.conversation.metadata.id}")
        else:
            # Set persona system prompt
            if persona in PERSONAS:
                persona_config = PERSONAS[persona]
                system_message = persona_config["system_message"]
                self.set_system_prompt(system_message)
                logger.info(f"Set system prompt for persona {persona.value} in conversation {self.conversation.metadata.id}")

    def set_system_prompt(self, content: str) -> Message:
        """Create or update the system prompt for the conversation."""
        sys_msg = self.conversation.get_system_message()
        if sys_msg is None:
            return self.add_system_message(content)

        # Update existing system message in-place
        sys_msg.content = content
        sys_msg.timestamp = datetime.now()
        self.conversation.metadata.updated_at = datetime.now()
        return sys_msg

    # ------------------------------------------------------------------
    # Reasoning feature
    # ------------------------------------------------------------------
    def _is_complex_task(
        self,
        prompt: str,
        settings: Optional[ChatSettings] = None,
    ) -> bool:
        """Return True if the prompt is complex according to the model."""
        settings = settings or self.conversation.settings
        classification_system = (
            "You are a classifier that decides whether a user's request "
            "requires multi-step reasoning. Respond with 'simple' if the "
            "task can be answered in a single response, else respond with "
            "'complex'. Respond with a single word ('simple' or 'complex')."
            "Question example: what is the capital of France?"
            "Answer example: 'simple'"
            "Question example: what should I do to get a job in the US?"
            "Answer example: 'complex'"
        )
        messages = [
            {"role": "system", "content": classification_system},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat_completion(
            messages=messages,
            model=settings.model,
            temperature=0.0,
            max_tokens=5,
        )
        decision = response.choices[0].message.content.strip().lower()
        return "complex" in decision

    def _describe_task(
        self,
        prompt: str,
        settings: Optional[ChatSettings] = None,
    ) -> str:
        """Ask the model to describe what the user wants to do."""
        settings = settings or self.conversation.settings
        sys_msg = (
            "You are an assistant that clarifies user intent. "
            "Summarize in one or two sentences what the user wants to "
            "achieve."
        )
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat_completion(
            messages=messages,
            model=settings.model,
            temperature=0.3,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()

    def _plan_steps(
        self,
        description: str,
        settings: Optional[ChatSettings] = None,
    ) -> List[str]:
        """Ask the model to lay out steps to solve the problem."""
        settings = settings or self.conversation.settings
        sys_msg = (
            "You are an expert planner. Given a problem description, "
            "produce an ordered list of clear, high-level steps to solve it. "
            "Respond with a numbered list."
        )
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": description},
        ]
        response = self.client.chat_completion(
            messages=messages,
            model=settings.model,
            temperature=0.3,
            max_tokens=300,
        )
        plan_text = response.choices[0].message.content.strip()
        # naive parsing: split by newline and keep non-empty lines
        steps: List[str] = []
        for line in plan_text.split("\n"):
            cleaned = line.strip(" -")
            if cleaned:
                steps.append(cleaned)
        if not steps:
            steps = [plan_text]
        return steps

    def _solve_step(
        self,
        step: str,
        context: str,
        settings: Optional[ChatSettings] = None,
    ) -> str:
        """Ask the model to solve a single step."""
        settings = settings or self.conversation.settings
        sys_msg = (
            "You are an expert problem solver. Provide a detailed answer "
            "for the given step in the context of the overall task."
        )
        user_msg = f"Overall task: {context}\n\nCurrent step: {step}"
        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
            model=settings.model,
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()

    def _optimize_answer(
        self,
        compiled_answer: str,
        settings: Optional[ChatSettings] = None,
    ) -> str:
        """Ask the model to optimize the compiled answer."""
        settings = settings or self.conversation.settings
        sys_msg = (
            "You are an assistant that edits and optimizes answers for "
            "clarity, conciseness, and completeness. Improve the following "
            "answer while keeping all important details."
        )
        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": compiled_answer},
            ],
            model=settings.model,
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()

    def chat_with_reasoning(
        self,
        user_message: str,
        settings_override: Optional[ChatSettings] = None,
    ) -> str:
        """Enhanced chat that performs multi-step reasoning when helpful."""
        settings = settings_override or self.conversation.settings

        # Record the user message in the main conversation
        self.add_user_message(user_message)

        # Decide complexity
        is_complex = self._is_complex_task(user_message, settings)

        if not is_complex:
            # Simple: fallback to normal flow
            return self.get_ai_response(settings)

        # Complex task – reasoning flow
        description = self._describe_task(user_message, settings)
        self.add_assistant_message(f"**Task summary:** {description}")

        steps = self._plan_steps(description, settings)
        self.add_assistant_message("**Proposed steps:**\n" + "\n".join(steps))

        step_answers: List[str] = []
        for idx, step in enumerate(steps, start=1):
            answer = self._solve_step(step, description, settings)
            step_answers.append(f"### Step {idx}: {step}\n{answer}")
            # Optionally add each step answer as assistant message
            self.add_assistant_message(step_answers[-1])

        compiled_answer = "\n\n".join(step_answers)
        optimized = self._optimize_answer(compiled_answer, settings)

        # Final optimized answer recorded and returned
        self.add_assistant_message(optimized)
        return optimized
