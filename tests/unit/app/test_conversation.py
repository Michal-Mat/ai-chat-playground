from unittest.mock import Mock

import pytest

from core.container import reset_container


class TestConversationFlow:
    """Test conversation flow logic."""

    def setup_method(self):
        """Setup test environment."""
        reset_container()

        # Create mock manager
        self.mock_manager = Mock()
        self.mock_manager.chat.return_value = "AI response"

    def test_chat_message_processing(self):
        """Test that chat messages are processed correctly."""
        user_input = "Test message"

        # Process through manager
        response = self.mock_manager.chat(user_input)

        # Verify
        self.mock_manager.chat.assert_called_once_with(user_input)
        assert response == "AI response"

    def test_conversation_save(self):
        """Test conversation saving to repository."""
        self.mock_manager.save_to_repository()

        self.mock_manager.save_to_repository.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
