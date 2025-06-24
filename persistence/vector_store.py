"""Light wrapper around QdrantClient for storing embeddings."""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams


class QdrantVectorStore:
    """Provide minimal upsert and search helpers."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "conversation_embeddings",
        vector_dim: int = 1536,
        distance: Distance = Distance.COSINE,
    ) -> None:
        self._client = QdrantClient(url=f"http://{host}:{port}")
        self._collection = collection_name

        # Create the collection if it does not exist.
        if collection_name not in self._client.get_collections().collections:
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_dim,
                    distance=distance,
                ),
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def upsert(
        self,
        vector_id: str,
        embedding: list[float],
        payload: dict | None = None,
    ) -> None:
        """Upsert a single embedding vector."""
        point = PointStruct(id=vector_id, vector=embedding, payload=payload)
        self._client.upsert(collection_name=self._collection, points=[point])

    def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        **kwargs,
    ):
        """Search for similar vectors and return the raw Qdrant response."""
        return self._client.search(
            collection_name=self._collection,
            query_vector=embedding,
            limit=top_k,
            **kwargs,
        )
