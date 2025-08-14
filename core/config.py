"""
Centralized Configuration Management

This module provides a singleton configuration manager that reads
environment variables from .env file with sensible defaults.
"""

import os
from typing import Any

from dotenv import load_dotenv


class AppConfig:
    """
    Centralized application configuration singleton.

    Reads configuration from environment variables with sensible defaults.
    Should be initialized once at application startup.
    """

    _instance: "AppConfig | None" = None
    _initialized: bool = False

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._load_environment()
            self._load_config()
            self._initialized = True

    def _load_environment(self) -> None:
        """Load environment variables from .env file if it exists."""
        load_dotenv()

    def _load_config(self) -> None:
        """Load all configuration values with defaults."""
        # OpenAI Configuration
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.openai_org_id: str = os.getenv("OPENAI_ORG_ID", "")

        # MongoDB Configuration
        self.mongo_uri: str = os.getenv(
            "MONGO_URI", "mongodb://localhost:27017"
        )
        self.mongo_db_name: str = os.getenv("MONGO_DB_NAME", "hugging_chat")
        self.mongo_collection_name: str = os.getenv(
            "MONGO_COLLECTION_NAME", "conversations"
        )

        # Qdrant Configuration
        self.qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
        self.qdrant_collection: str = os.getenv(
            "QDRANT_COLLECTION", "conversation_embeddings"
        )
        self.qdrant_vector_dim: int = int(
            os.getenv("QDRANT_VECTOR_DIM", "1536")
        )

        # AI Model Configuration
        self.embedding_model: str = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.default_chat_model: str = os.getenv(
            "DEFAULT_CHAT_MODEL", "gpt-3.5-turbo"
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        setattr(self, key, value)

    def validate_required(self) -> None:
        """Validate that required configuration values are present."""
        required_configs = [
            ("openai_api_key", "OPENAI_API_KEY"),
        ]

        missing_configs = []
        for attr_name, env_name in required_configs:
            if not getattr(self, attr_name):
                missing_configs.append(env_name)

        if missing_configs:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_configs)}"
            )


# Global config instance
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
    AppConfig._instance = None
    AppConfig._initialized = False
