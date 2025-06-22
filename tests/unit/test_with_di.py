"""
Example tests showing how dependency injection makes testing easier.

This demonstrates mocking dependencies and testing in isolation.
"""

import pytest
from unittest.mock import Mock, MagicMock
from core.container import get_container, reset_container
from conversations.manager import ConversationManager


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
            'openai_client',
            lambda: self.mock_openai_client
        )
        container.register_singleton(
            'conversation_repository',
            lambda: self.mock_repository
        )

    def test_chat_with_mocked_dependencies(self):
        """Test chat functionality with mocked dependencies."""
        # Create manager with injected dependencies
        container = get_container()
        manager = ConversationManager(
            client=container.get('openai_client'),
            repository=container.get('conversation_repository')
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
            client=container.get('openai_client'),
            repository=container.get('conversation_repository')
        )

        # Add a message and save
        manager.add_user_message("Test message")
        manager.save_to_repository()

        # Verify repository was called
        self.mock_repository.save.assert_called_once()


class TestServiceContainer:
    """Test the service container itself."""

    def setup_method(self):
        """Reset container for each test."""
        reset_container()

    def test_singleton_behavior(self):
        """Test that singletons return the same instance."""
        container = get_container()

        # Register a singleton
        call_count = 0
        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        container.register_singleton('test_service', factory)

        # Get service multiple times
        instance1 = container.get('test_service')
        instance2 = container.get('test_service')

        # Should be same instance
        assert instance1 == instance2 == "instance_1"
        assert call_count == 1  # Factory called only once

    def test_factory_behavior(self):
        """Test that factories return new instances."""
        container = get_container()

        # Register a factory
        call_count = 0
        def factory():
            nonlocal call_count
            call_count += 1
            return f"instance_{call_count}"

        container.register_factory('test_service', factory)

        # Get service multiple times
        instance1 = container.get('test_service')
        instance2 = container.get('test_service')

        # Should be different instances
        assert instance1 == "instance_1"
        assert instance2 == "instance_2"
        assert call_count == 2  # Factory called twice


# Example of how to test individual services
class TestPDFIngestService:
    """Test PDF ingest service with mocked dependencies."""

    def setup_method(self):
        """Setup mocked dependencies."""
        reset_container()

        # Mock vector store
        self.mock_vector_store = Mock()

        # Register mock
        container = get_container()
        container.register_singleton(
            'vector_store',
            lambda: self.mock_vector_store
        )

    def test_pdf_ingestion_mocked(self):
        """Test PDF ingestion with mocked vector store."""
        from pipelines.pdf_ingest_service import PDFIngestService

        # Create service with mocked dependency
        container = get_container()
        service = PDFIngestService(
            vector_store=container.get('vector_store'),
            embed_model_name='test-model'  # Mock model name
        )

        # Test would normally process a PDF, but we're just testing
        # the dependency injection pattern here
        assert service.vector_store == self.mock_vector_store


if __name__ == "__main__":
    pytest.main([__file__])