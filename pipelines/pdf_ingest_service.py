from __future__ import annotations

import uuid
from pathlib import Path
from typing import List

import pdfplumber  # type: ignore
from pdf2image import convert_from_path  # type: ignore
import pytesseract  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from transformers import AutoTokenizer  # type: ignore

# Import directly to avoid circular import via persistence.__init__
from persistence.vector_store import QdrantVectorStore

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class PDFIngestService:
    """Pipeline to turn a PDF into embedded chunks stored in Qdrant."""

    def __init__(
        self,
        vector_store: QdrantVectorStore | None = None,
        embed_model_name: str = DEFAULT_EMBED_MODEL,
    ) -> None:
        self.vector_store = vector_store or QdrantVectorStore()
        self.embedder = SentenceTransformer(embed_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(embed_model_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def ingest_pdf(
        self,
        file_path: str | Path,
        chunk_size: int = 200,
        overlap: int = 40,
    ) -> int:
        """Extract, chunk, embed, and store a PDF.

        Args:
            file_path: Path to the PDF file.
            chunk_size: Maximum tokens per chunk.
            overlap: Token overlap between consecutive chunks.

        Returns:
            Number of chunks stored.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        # 1. Extract text (with OCR fallback per page)
        full_text = self._extract_text(file_path)

        # 2. Split into chunks
        chunks = self._chunk_text(full_text, chunk_size, overlap)

        # 3. Embed and upsert
        num_chunks = 0
        for chunk_text in chunks:
            emb = self.embedder.encode(chunk_text).tolist()
            vec_id = str(uuid.uuid4())
            payload = {
                "source": str(file_path.name),
                "text": chunk_text,
            }
            self.vector_store.upsert(vec_id, emb, payload)
            num_chunks += 1

        return num_chunks

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _extract_text(self, pdf_path: Path) -> str:
        """Extract text from a PDF, using OCR when necessary."""
        parts: List[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(text)
                else:
                    # OCR fallback for scanned page
                    image = convert_from_path(  # noqa: E501
                        str(pdf_path),
                        first_page=page.page_number,
                        last_page=page.page_number,
                    )[0]
                    ocr_text = pytesseract.image_to_string(image)
                    parts.append(ocr_text)
        return "\n".join(parts)

    def _chunk_text(
        self, text: str, chunk_size: int = 200, overlap: int = 40
    ) -> List[str]:
        """Split text into token-aware chunks."""
        words = text.split()
        chunks: List[str] = []
        i = 0
        while i < len(words):
            # Expand window until token limit reached
            current_words: List[str] = []
            token_count = 0
            while i < len(words) and token_count < chunk_size:
                current_words.append(words[i])
                token_ids = self.tokenizer(  # noqa: E501
                    " ".join(current_words)
                )["input_ids"]
                token_count = len(token_ids)
                if token_count >= chunk_size:
                    current_words.pop()  # remove last word that caused overflow
                    break
                i += 1
            chunk_text = " ".join(current_words)
            if chunk_text:
                chunks.append(chunk_text)
            # move index back by overlap tokens
            i = max(i - overlap, i)  # noqa: E501
            i += 1
        return chunks
