"""MongoDB-based repository for conversations."""

from typing import Optional, List

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection

from conversations.models import Conversation


class ConversationRepository:
    """Provide basic CRUD operations for Conversation objects."""

    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "hugging_chat",
        collection_name: str = "conversations",
    ) -> None:
        self._client = MongoClient(mongo_uri)
        self._collection: Collection = self._client[db_name][collection_name]

        # Ensure an index on the conversation ID field for quick look-ups.
        self._collection.create_index(
            [("metadata.id", ASCENDING)], unique=True, background=True
        )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def insert(self, conversation: Conversation) -> str:
        """Insert a new conversation document and return its ID."""
        self._collection.insert_one(conversation.export_to_dict())
        return conversation.metadata.id

    def save(self, conversation: Conversation) -> None:
        """Upsert the entire conversation document."""
        self._collection.replace_one(
            {"metadata.id": conversation.metadata.id},
            conversation.export_to_dict(),
            upsert=True,
        )

    def get(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by its identifier."""
        doc = self._collection.find_one({"metadata.id": conversation_id})
        if doc is None:
            return None
        return Conversation.from_dict(doc)  # type: ignore[arg-type]

    def list(self, limit: int = 50) -> List[Conversation]:
        """Return a subset of recent conversations (newest first)."""
        cursor = self._collection.find().sort("metadata.updated_at", -1).limit(limit)
        return [Conversation.from_dict(doc) for doc in cursor]  # type: ignore[arg-type]

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation; return True if one was removed."""
        result = self._collection.delete_one({"metadata.id": conversation_id})
        return result.deleted_count == 1
