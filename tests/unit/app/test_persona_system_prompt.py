"""
Tests for persona system prompt integration.

This module tests that when a persona is selected, the appropriate
system prompt is automatically set in the conversation.
"""

import pytest
from unittest.mock import Mock
from conversations.manager import ConversationManager
from conversations.types import Persona
from conversations.personas.personas import PERSONAS


class TestPersonaSystemPromptIntegration:
    """Test persona system prompt integration functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock OpenAI client for testing."""
        return Mock()

    @pytest.fixture
    def conversation_manager(self, mock_client):
        """Create a ConversationManager instance for testing."""
        return ConversationManager(client=mock_client)

    def test_initial_state_has_no_persona_or_system_message(self, conversation_manager):
        """Test that a new conversation has no persona or system message."""
        assert conversation_manager.conversation.settings.persona is None
        assert conversation_manager.conversation.get_system_message() is None

    def test_setting_persona_updates_system_prompt(self, conversation_manager):
        """Test that setting a persona automatically updates the system prompt."""
        # Update to technical persona
        conversation_manager.update_settings(persona=Persona.TECHNICAL)

        # Check that persona was set
        assert conversation_manager.conversation.settings.persona == Persona.TECHNICAL

        # Check that system message was automatically set
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg is not None
        assert sys_msg.content == PERSONAS[Persona.TECHNICAL]["system_message"]

    def test_changing_persona_updates_system_prompt(self, conversation_manager):
        """Test that changing from one persona to another updates the system prompt."""
        # Set initial persona
        conversation_manager.update_settings(persona=Persona.CREATIVE)
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg.content == PERSONAS[Persona.CREATIVE]["system_message"]

        # Change to different persona
        conversation_manager.update_settings(persona=Persona.TEACHER)
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg.content == PERSONAS[Persona.TEACHER]["system_message"]

    def test_clearing_persona_removes_persona_system_prompt(self, conversation_manager):
        """Test that clearing a persona removes the persona-specific system prompt."""
        # Set a persona first
        conversation_manager.update_settings(persona=Persona.ASSISTANT)
        assert conversation_manager.conversation.get_system_message() is not None

        # Clear the persona
        conversation_manager.update_settings(persona=None)

        # Check persona is cleared
        assert conversation_manager.conversation.settings.persona is None

        # Check that persona system message was removed
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg is None

    def test_custom_system_prompt_not_removed_when_clearing_persona(self, conversation_manager):
        """Test that custom system prompts are preserved when clearing persona."""
        # Set a custom system prompt first
        custom_prompt = "You are a custom AI assistant with special instructions."
        conversation_manager.set_system_prompt(custom_prompt)

        # Then set a persona
        conversation_manager.update_settings(persona=Persona.TECHNICAL)

        # System prompt should now be the persona one
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg.content == PERSONAS[Persona.TECHNICAL]["system_message"]

        # Clear the persona
        conversation_manager.update_settings(persona=None)

        # The persona system prompt should be removed, leaving no system message
        # (since we overwrote the custom one)
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg is None

    def test_all_personas_have_valid_system_messages(self, conversation_manager):
        """Test that all defined personas have valid system messages."""
        for persona in Persona:
            # Set the persona
            conversation_manager.update_settings(persona=persona)

            # Check that system message was set correctly
            sys_msg = conversation_manager.conversation.get_system_message()
            assert sys_msg is not None
            assert sys_msg.content == PERSONAS[persona]["system_message"]
            assert len(sys_msg.content.strip()) > 0

            # Clear for next iteration
            conversation_manager.update_settings(persona=None)

    def test_persona_system_prompt_persists_across_settings_updates(self, conversation_manager):
        """Test that persona system prompts persist when other settings change."""
        # Set a persona
        conversation_manager.update_settings(persona=Persona.PERSONAL_ASSISTANT)
        original_system_message = conversation_manager.conversation.get_system_message().content

        # Update other settings (not persona)
        conversation_manager.update_settings(
            model="gpt-4",
            temperature=0.5,
            reasoning=True
        )

        # Persona and system message should remain unchanged
        assert conversation_manager.conversation.settings.persona == Persona.PERSONAL_ASSISTANT
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg.content == original_system_message

    def test_persona_update_with_existing_conversation_messages(self, conversation_manager):
        """Test persona updates work correctly even with existing conversation messages."""
        # Add some conversation messages first
        conversation_manager.add_user_message("Hello, how are you?")
        conversation_manager.add_assistant_message("I'm doing well, thank you!")

        # Now set a persona
        conversation_manager.update_settings(persona=Persona.CREATIVE)

        # System message should be added
        sys_msg = conversation_manager.conversation.get_system_message()
        assert sys_msg is not None
        assert sys_msg.content == PERSONAS[Persona.CREATIVE]["system_message"]

        # Original messages should still be there
        messages = conversation_manager.get_messages(include_system=False)
        assert len(messages) == 2
        assert messages[0].content == "Hello, how are you?"
        assert messages[1].content == "I'm doing well, thank you!"

    def test_persona_none_vs_no_persona_setting(self, conversation_manager):
        """Test the difference between explicitly setting persona=None vs not setting it."""
        # Initially no persona
        assert conversation_manager.conversation.settings.persona is None

        # Set a persona
        conversation_manager.update_settings(persona=Persona.TECHNICAL)
        assert conversation_manager.conversation.settings.persona == Persona.TECHNICAL

        # Explicitly set to None
        conversation_manager.update_settings(persona=None)
        assert conversation_manager.conversation.settings.persona is None

        # Update other settings without mentioning persona
        conversation_manager.update_settings(model="gpt-4")
        assert conversation_manager.conversation.settings.persona is None  # Should remain None