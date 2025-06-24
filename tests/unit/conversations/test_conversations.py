"""
Example tests showing how dependency injection makes testing easier.

This demonstrates mocking dependencies and testing in isolation.
"""

from unittest.mock import MagicMock, Mock

import pytest

from conversations.manager import ConversationManager
from core.container import get_container, reset_container


class TestConversationManagerWithDI:
    """Test ConversationManager using dependency injection."""

    def setup_method(self):
        """Setup test environment with mocked dependencies."""
        # Reset container for clean state
        reset_container()

        # Create mock dependencies
        self.mock_openai_client = Mock()
        self.mock_repository = Mock()

        # Setup mock responses
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test AI response"
        self.mock_openai_client.chat_completion.return_value = mock_response

        # Register mocked services
        container = get_container()
        container.register_singleton(
            "openai_client", lambda: self.mock_openai_client
        )
        container.register_singleton(
            "conversation_repository", lambda: self.mock_repository
        )

    def test_chat_with_mocked_dependencies(self):
        """Test chat functionality with mocked dependencies."""
        # Create manager with injected dependencies
        container = get_container()
        manager = ConversationManager(
            client=container.get("openai_client"),
            repository=container.get("conversation_repository"),
        )

        # Test chat
        response = manager.chat("Hello, AI!")

        # Verify interactions
        assert response == "Test AI response"
        self.mock_openai_client.chat_completion.assert_called_once()

        # Verify message was added
        messages = manager.get_messages()
        assert len(messages) == 2  # user + assistant
        assert messages[0].content == "Hello, AI!"
        assert messages[1].content == "Test AI response"

    def test_save_to_repository(self):
        """Test saving conversation with mocked repository."""
        container = get_container()
        manager = ConversationManager(
            client=container.get("openai_client"),
            repository=container.get("conversation_repository"),
        )

        # Add a message and save
        manager.add_user_message("Test message")
        manager.save_to_repository()

        # Verify repository was called
        self.mock_repository.save.assert_called_once()


# Example of how to test individual services


if __name__ == "__main__":
    pytest.main([__file__])
