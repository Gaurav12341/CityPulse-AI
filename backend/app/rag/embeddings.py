"""Embedding services for the CityPulse RAG pipeline."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer


load_dotenv()

EMBEDDING_MODEL_ENV_VAR = "EMBEDDING_MODEL_NAME"


@dataclass(frozen=True)
class EmbeddedDocument:
    """A document chunk paired with its vector embedding."""

    document: Document
    embedding: list[float]

    @property
    def metadata(self) -> dict:
        """Return the source document metadata preserved for vector storage."""
        return self.document.metadata


class SentenceTransformerEmbeddingService:
    """Generate embeddings for RAG documents using Sentence Transformers."""

    def __init__(self, model_name: str | None = None) -> None:
        """Initialize the embedding service.

        Args:
            model_name: Optional Sentence Transformers model name. If omitted,
                the value is read from ``EMBEDDING_MODEL_NAME``.

        Raises:
            ValueError: If no embedding model name is configured.
            RuntimeError: If the Sentence Transformers model cannot be loaded.
        """
        self.model_name = model_name or os.getenv(EMBEDDING_MODEL_ENV_VAR)

        if not self.model_name:
            raise ValueError(
                "Embedding model name is required. Set "
                f"{EMBEDDING_MODEL_ENV_VAR} in the environment or pass "
                "model_name explicitly."
            )

        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model '{self.model_name}'."
            ) from exc

    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[EmbeddedDocument]:
        """Generate embeddings for chunked LangChain documents.

        Args:
            documents: Chunked LangChain ``Document`` objects, typically
                produced by ``chunk_documents``.

        Returns:
            A list of ``EmbeddedDocument`` objects containing the original
            document chunk, its metadata, and its embedding vector.

        Raises:
            ValueError: If a document has empty page content.
            RuntimeError: If embedding generation fails.
        """
        if not documents:
            return []

        texts = [self._get_document_text(document) for document in documents]

        try:
            embeddings = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise RuntimeError("Failed to generate document embeddings.") from exc

        return [
            EmbeddedDocument(
                document=document,
                embedding=embedding.tolist(),
            )
            for document, embedding in zip(documents, embeddings)
        ]

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding vector for a retrieval query.

        Args:
            query: User question or search text to embed.

        Returns:
            A normalized embedding vector.

        Raises:
            ValueError: If the query is empty.
            RuntimeError: If embedding generation fails.
        """
        query_text = query.strip()
        if not query_text:
            raise ValueError("query cannot be empty.")

        try:
            embedding = self._model.encode(
                query_text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise RuntimeError("Failed to generate query embedding.") from exc

        return embedding.tolist()

    @staticmethod
    def _get_document_text(document: Document) -> str:
        """Validate and return the text content from a document chunk."""
        text = document.page_content.strip()
        if not text:
            filename = document.metadata.get("filename", "unknown")
            raise ValueError(
                f"Document chunk from '{filename}' has empty page content."
            )

        return text
