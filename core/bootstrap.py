"""
Bootstrap module for dependency injection setup.

This module registers all services with the container and provides
factory functions for creating properly configured instances.
"""

from conversations.manager import ConversationManager
from core.config import AppConfig, get_config
from core.container import get_container
from integrations.openai.client import OpenAIClient
from persistence.mongo_repository import ConversationRepository
from persistence.vector_store import QdrantVectorStore
from pipelines.pdf_ingest_service import PDFIngestService


def create_openai_client(config: AppConfig) -> OpenAIClient:
    """Factory function for OpenAI client."""
    return OpenAIClient(
        api_key=config.openai_api_key,
        organization=config.openai_org_id,
    )


def create_conversation_repository(
    config: AppConfig,
) -> ConversationRepository:
    """Factory function for conversation repository."""
    return ConversationRepository(
        mongo_uri=config.mongo_uri,
        db_name=config.mongo_db_name,
        collection_name=config.mongo_collection_name,
    )


def create_vector_store(config: AppConfig) -> QdrantVectorStore:
    """Factory function for vector store."""
    return QdrantVectorStore(
        host=config.qdrant_host,
        port=config.qdrant_port,
        collection_name=config.qdrant_collection,
        vector_dim=config.qdrant_vector_dim,
    )


def create_pdf_ingest_service(config: AppConfig) -> PDFIngestService:
    """Factory function for PDF ingest service."""
    container = get_container()
    vector_store = container.get("vector_store")
    return PDFIngestService(
        vector_store=vector_store,
        embed_model_name=config.embedding_model,
    )


def create_conversation_manager(config: AppConfig) -> ConversationManager:
    """Factory function for conversation manager."""
    container = get_container()
    openai_client = container.get("openai_client")
    repository = container.get("conversation_repository")

    return ConversationManager(
        client=openai_client,
        model=config.default_chat_model,
        repository=repository,
    )


def register_services(config: AppConfig) -> None:
    """Register all services with the container."""
    container = get_container()

    # Register config as singleton
    container.register_singleton("config", lambda: config)

    # Register core services as singletons with config injection
    container.register_singleton(
        "openai_client", lambda: create_openai_client(config)
    )
    container.register_singleton(
        "conversation_repository",
        lambda: create_conversation_repository(config),
    )
    container.register_singleton(
        "vector_store", lambda: create_vector_store(config)
    )
    container.register_singleton(
        "pdf_ingest_service", lambda: create_pdf_ingest_service(config)
    )

    # Register conversation manager as factory (new instance per use)
    container.register_factory(
        "conversation_manager", lambda: create_conversation_manager(config)
    )


def setup_di() -> None:
    """Setup dependency injection for the application."""
    # Initialize config once at startup
    config = get_config()
    config.validate_required()

    # Register all services with the initialized config
    register_services(config=config)


# Auto-register services when module is imported
setup_di()
