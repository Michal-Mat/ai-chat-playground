"""
Bootstrap module for dependency injection setup.

This module registers all services with the container and provides
factory functions for creating properly configured instances.
"""

from conversations.manager import ConversationManager
from core.container import get_config, get_container
from integrations.openai.client import OpenAIClient
from persistence.mongo_repository import ConversationRepository
from persistence.vector_store import QdrantVectorStore
from pipelines.pdf_ingest_service import PDFIngestService


def create_openai_client() -> OpenAIClient:
    """Factory function for OpenAI client."""
    return OpenAIClient(
        api_key=get_config("openai_api_key"),
        organization=get_config("openai_org_id"),
    )


def create_conversation_repository() -> ConversationRepository:
    """Factory function for conversation repository."""
    return ConversationRepository(
        mongo_uri=get_config("mongo_uri"),
        db_name=get_config("mongo_db_name"),
        collection_name=get_config("mongo_collection_name"),
    )


def create_vector_store() -> QdrantVectorStore:
    """Factory function for vector store."""
    return QdrantVectorStore(
        host=get_config("qdrant_host"),
        port=get_config("qdrant_port"),
        collection_name=get_config("qdrant_collection"),
        vector_dim=get_config("qdrant_vector_dim"),
    )


def create_pdf_ingest_service() -> PDFIngestService:
    """Factory function for PDF ingest service."""
    container = get_container()
    vector_store = container.get("vector_store")
    return PDFIngestService(
        vector_store=vector_store,
        embed_model_name=get_config("embedding_model"),
    )


def create_conversation_manager() -> ConversationManager:
    """Factory function for conversation manager."""
    container = get_container()
    openai_client = container.get("openai_client")
    repository = container.get("conversation_repository")

    return ConversationManager(
        client=openai_client,
        model=get_config("default_chat_model"),
        repository=repository,
    )


def register_services() -> None:
    """Register all services with the container."""
    container = get_container()

    # Register core services as singletons

    container.register_singleton("openai_client", create_openai_client)
    container.register_singleton(
        "conversation_repository", create_conversation_repository
    )
    container.register_singleton("vector_store", create_vector_store)
    container.register_singleton(
        "pdf_ingest_service", create_pdf_ingest_service
    )

    # Register conversation manager as factory (new instance per use)
    container.register_factory(
        "conversation_manager", create_conversation_manager
    )


def setup_di() -> None:
    """Setup dependency injection for the application."""
    register_services()


# Auto-register services when module is imported
setup_di()
