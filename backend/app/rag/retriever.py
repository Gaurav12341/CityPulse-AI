"""Document retrieval utilities for the CityPulse RAG pipeline."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.embeddings import SentenceTransformerEmbeddingService
from app.rag.vector_store import FaissVectorStore, SearchResult


DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_TOP_K = 3
METADATA_FILTER_FETCH_MULTIPLIER = 5


def chunk_documents(
    documents: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Split LangChain documents into metadata-preserving text chunks.

    Args:
        documents: Source documents returned by the municipal document loader.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters repeated between adjacent chunks.

    Returns:
        A list of chunked LangChain ``Document`` objects with source metadata
        preserved.

    Raises:
        ValueError: If chunking parameters are invalid.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return text_splitter.split_documents(documents)


class SemanticRetriever:
    """Retrieve municipal document chunks using semantic vector search."""

    def __init__(
        self,
        embedding_service: SentenceTransformerEmbeddingService,
        vector_store: FaissVectorStore,
    ) -> None:
        """Initialize the semantic retriever.

        Args:
            embedding_service: Service used to embed user queries.
            vector_store: FAISS-backed vector store containing document chunks.
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        """Retrieve document chunks most relevant to a query.

        Args:
            query: User question or search text.
            top_k: Maximum number of results to return.
            metadata_filter: Optional exact-match metadata filters, such as
                ``{"filename": "garbage_collection.txt"}``.

        Returns:
            Ranked search results with source documents, metadata, and scores.

        Raises:
            ValueError: If the query, ``top_k``, or metadata filter is invalid.
            RuntimeError: If query embedding or vector search fails.
        """
        query_text = query.strip()
        if not query_text:
            raise ValueError("query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self._validate_metadata_filter(metadata_filter)

        query_embedding = self.embedding_service.embed_query(query_text)
        fetch_count = self._get_fetch_count(top_k, metadata_filter)
        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=fetch_count,
        )

        if metadata_filter:
            results = [
                result
                for result in results
                if self._matches_metadata_filter(
                    result.document,
                    metadata_filter,
                )
            ]

        return results[:top_k]

    @staticmethod
    def _get_fetch_count(
        top_k: int,
        metadata_filter: dict[str, str] | None,
    ) -> int:
        """Return the number of raw vector results to fetch."""
        if metadata_filter:
            return top_k * METADATA_FILTER_FETCH_MULTIPLIER

        return top_k

    @staticmethod
    def _validate_metadata_filter(
        metadata_filter: dict[str, str] | None,
    ) -> None:
        """Validate optional metadata filter values."""
        if metadata_filter is None:
            return

        if not metadata_filter:
            raise ValueError("metadata_filter cannot be empty.")

        for key, value in metadata_filter.items():
            if not key.strip():
                raise ValueError("metadata_filter keys cannot be empty.")

            if not value.strip():
                raise ValueError(
                    f"metadata_filter value for '{key}' cannot be empty."
                )

    @staticmethod
    def _matches_metadata_filter(
        document: Document,
        metadata_filter: dict[str, str],
    ) -> bool:
        """Return whether a document matches all metadata filters."""
        return all(
            str(document.metadata.get(key)) == value
            for key, value in metadata_filter.items()
        )
