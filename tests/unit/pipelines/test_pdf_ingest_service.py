from unittest.mock import Mock

from core.container import get_container, reset_container


class TestPDFIngestService:
    """Test PDF ingest service with mocked dependencies."""

    def setup_method(self):
        """Setup mocked dependencies."""
        reset_container()

        # Mock vector store
        self.mock_vector_store = Mock()

        # Register mock
        container = get_container()
        container.register_singleton("vector_store", lambda: self.mock_vector_store)

    def test_pdf_ingestion_mocked(self):
        """Test PDF ingestion with mocked vector store."""
        from pipelines.pdf_ingest_service import PDFIngestService
        from unittest.mock import patch

        # Create service with mocked dependency and mocked SentenceTransformer
        container = get_container()

        with patch(
            "pipelines.pdf_ingest_service.SentenceTransformer"
        ) as mock_sentence_transformer:
            # Mock the SentenceTransformer
            mock_embedder = Mock()
            mock_sentence_transformer.return_value = mock_embedder

            service = PDFIngestService(
                vector_store=container.get("vector_store"),
                embed_model_name="sentence-transformers/all-MiniLM-L6-v2",  # Use real model name
            )

            # Test would normally process a PDF, but we're just testing
            # the dependency injection pattern here
            assert service.vector_store == self.mock_vector_store
            assert service.embedder == mock_embedder

            # Verify SentenceTransformer was called with correct model name
            mock_sentence_transformer.assert_called_once_with(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
