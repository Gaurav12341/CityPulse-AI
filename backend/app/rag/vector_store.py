"""FAISS vector storage utilities for the CityPulse RAG pipeline."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from dotenv import load_dotenv
from langchain_core.documents import Document

from app.rag.embeddings import EmbeddedDocument


load_dotenv()

FAISS_INDEX_DIR_ENV_VAR = "FAISS_INDEX_DIR"
DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "faiss_index"
FAISS_INDEX_FILE = "index.faiss"
DOCUMENT_STORE_FILE = "documents.json"


@dataclass(frozen=True)
class SearchResult:
    """A retrieved document chunk and its vector similarity score."""

    document: Document
    score: float


def get_default_index_dir() -> Path:
    """Return the configured FAISS index directory."""
    configured_dir = os.getenv(FAISS_INDEX_DIR_ENV_VAR)
    if configured_dir:
        return Path(configured_dir)

    return DEFAULT_INDEX_DIR


class FaissVectorStore:
    """Persist and query embedded RAG document chunks with FAISS."""

    def __init__(self, index_dir: Path | None = None) -> None:
        """Initialize a FAISS vector store.

        Args:
            index_dir: Directory used to persist the FAISS index and document
                metadata store.
        """
        self.index_dir = Path(index_dir) if index_dir else get_default_index_dir()
        self.index_path = self.index_dir / FAISS_INDEX_FILE
        self.documents_path = self.index_dir / DOCUMENT_STORE_FILE
        self._index: faiss.Index | None = None
        self._documents: list[Document] = []

    def build(self, embedded_documents: list[EmbeddedDocument]) -> None:
        """Build an in-memory FAISS index from embedded document chunks.

        Args:
            embedded_documents: Documents paired with embedding vectors.

        Raises:
            ValueError: If no embeddings are provided or vector dimensions are
                inconsistent.
        """
        vectors = self._to_vector_matrix(embedded_documents)

        vector_dimension = vectors.shape[1]
        index = faiss.IndexFlatIP(vector_dimension)
        index.add(vectors)

        self._index = index
        self._documents = [
            embedded_document.document
            for embedded_document in embedded_documents
        ]

    def save(self) -> None:
        """Persist the current FAISS index and document store to disk.

        Raises:
            RuntimeError: If the vector store has not been built or loaded.
        """
        self._ensure_ready()
        self.index_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self._index, str(self.index_path))
        self.documents_path.write_text(
            json.dumps(
                [
                    {
                        "page_content": document.page_content,
                        "metadata": document.metadata,
                    }
                    for document in self._documents
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load(self) -> None:
        """Load a persisted FAISS index and document store from disk.

        Raises:
            FileNotFoundError: If the index or document store file is missing.
            RuntimeError: If loading fails or stored counts are inconsistent.
        """
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index file does not exist: {self.index_path}"
            )

        if not self.documents_path.exists():
            raise FileNotFoundError(
                f"Document store file does not exist: {self.documents_path}"
            )

        try:
            index = faiss.read_index(str(self.index_path))
            stored_documents = json.loads(
                self.documents_path.read_text(encoding="utf-8")
            )
        except Exception as exc:
            raise RuntimeError("Failed to load FAISS vector store.") from exc

        documents = [
            Document(
                page_content=item["page_content"],
                metadata=item.get("metadata", {}),
            )
            for item in stored_documents
        ]

        if index.ntotal != len(documents):
            raise RuntimeError(
                "FAISS index and document store contain different item counts."
            )

        self._index = index
        self._documents = documents

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[SearchResult]:
        """Return the most similar document chunks for a query embedding.

        Args:
            query_embedding: Embedding vector generated from a user query.
            top_k: Maximum number of chunks to return.

        Returns:
            Ranked search results with source documents and similarity scores.

        Raises:
            ValueError: If ``top_k`` or the query embedding is invalid.
            RuntimeError: If the vector store is not ready.
        """
        self._ensure_ready()

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if not query_embedding:
            raise ValueError("query_embedding cannot be empty.")

        query_vector = np.asarray([query_embedding], dtype=np.float32)
        if query_vector.shape[1] != self._index.d:
            raise ValueError(
                "query_embedding dimension does not match FAISS index "
                f"dimension: {query_vector.shape[1]} != {self._index.d}."
            )

        scores, indices = self._index.search(query_vector, top_k)

        results: list[SearchResult] = []
        for score, index_position in zip(scores[0], indices[0]):
            if index_position == -1:
                continue

            results.append(
                SearchResult(
                    document=self._documents[index_position],
                    score=float(score),
                )
            )

        return results

    @property
    def document_count(self) -> int:
        """Return the number of document chunks currently in the store."""
        return len(self._documents)

    def _ensure_ready(self) -> None:
        """Validate that the vector store has an index and documents loaded."""
        if self._index is None:
            raise RuntimeError("FAISS vector store has not been built or loaded.")

        if not self._documents:
            raise RuntimeError("FAISS vector store contains no documents.")

    @staticmethod
    def _to_vector_matrix(
        embedded_documents: list[EmbeddedDocument],
    ) -> np.ndarray[Any, np.dtype[np.float32]]:
        """Convert embedded documents into a FAISS-compatible matrix."""
        if not embedded_documents:
            raise ValueError("embedded_documents cannot be empty.")

        vectors = [
            embedded_document.embedding
            for embedded_document in embedded_documents
        ]
        vector_lengths = {len(vector) for vector in vectors}

        if 0 in vector_lengths:
            raise ValueError("Embeddings cannot be empty vectors.")

        if len(vector_lengths) != 1:
            raise ValueError("All embeddings must have the same dimension.")

        return np.asarray(vectors, dtype=np.float32)
