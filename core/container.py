"""
Service Container for Dependency Injection

This module implements a service locator pattern with factory support
for managing application dependencies in a centralized way.
"""

import os
from typing import Any, Dict, Optional, Callable, TypeVar
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ServiceConfig:
    """Configuration for a service registration."""
    factory: Callable[[], Any]
    singleton: bool = True
    initialized: bool = field(default=False, init=False)
    instance: Any = field(default=None, init=False)


class ServiceContainer:
    """
    Service container implementing the Service Locator pattern.

    Supports both singleton and factory-created instances with
    configuration-driven dependency management.
    """

    def __init__(self):
        self._services: Dict[str, ServiceConfig] = {}
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        self._config = {
            # OpenAI Configuration
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'openai_org_id': os.getenv('OPENAI_ORG_ID'),

            # MongoDB Configuration
            'mongo_uri': os.getenv(
                'MONGO_URI', 'mongodb://localhost:27017'
            ),
            'mongo_db_name': os.getenv('MONGO_DB_NAME', 'hugging_chat'),
            'mongo_collection_name': os.getenv(
                'MONGO_COLLECTION_NAME', 'conversations'
            ),

            # Qdrant Configuration
            'qdrant_host': os.getenv('QDRANT_HOST', 'localhost'),
            'qdrant_port': int(os.getenv('QDRANT_PORT', '6333')),
            'qdrant_collection': os.getenv(
                'QDRANT_COLLECTION', 'conversation_embeddings'
            ),
            'qdrant_vector_dim': int(os.getenv('QDRANT_VECTOR_DIM', '1536')),

            # AI Model Configuration
            'embedding_model': os.getenv(
                'EMBEDDING_MODEL',
                'sentence-transformers/all-MiniLM-L6-v2'
            ),
            'default_chat_model': os.getenv(
                'DEFAULT_CHAT_MODEL', 'gpt-3.5-turbo'
            ),
        }

    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """Register a singleton service."""
        self._services[name] = ServiceConfig(factory=factory, singleton=True)
        logger.debug(f"Registered singleton service: {name}")

    def register_factory(self, name: str, factory: Callable[[], T]) -> None:
        """Register a factory service (new instance each time)."""
        self._services[name] = ServiceConfig(factory=factory, singleton=False)
        logger.debug(f"Registered factory service: {name}")

    def get(self, name: str) -> Any:
        """Get a service instance."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        service_config = self._services[name]

        if service_config.singleton:
            if not service_config.initialized:
                service_config.instance = service_config.factory()
                service_config.initialized = True
                logger.debug(f"Created singleton instance for: {name}")
            return service_config.instance
        else:
            # Create new instance each time for factory services
            return service_config.factory()

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    def reset_singleton(self, name: str) -> None:
        """Reset a singleton service (useful for testing)."""
        if name in self._services and self._services[name].singleton:
            self._services[name].initialized = False
            self._services[name].instance = None
            logger.debug(f"Reset singleton service: {name}")

    def clear_all(self) -> None:
        """Clear all services (useful for testing)."""
        self._services.clear()
        logger.debug("Cleared all services")


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container instance."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    _container = None


# Convenience functions
def register_singleton(name: str, factory: Callable[[], T]) -> None:
    """Register a singleton service."""
    get_container().register_singleton(name, factory)


def register_factory(name: str, factory: Callable[[], T]) -> None:
    """Register a factory service."""
    get_container().register_factory(name, factory)


def get_service(name: str) -> Any:
    """Get a service instance."""
    return get_container().get(name)


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return get_container().get_config(key, default)