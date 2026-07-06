"""RAG orchestration service for municipal knowledge answers."""

import re

from app.rag.embeddings import SentenceTransformerEmbeddingService
from app.rag.loader import load_municipal_documents
from app.rag.prompt import build_rag_prompt
from app.rag.retriever import DEFAULT_TOP_K, SemanticRetriever, chunk_documents
from app.rag.vector_store import FaissVectorStore, SearchResult
from app.services.gemini_service import ask_gemini


_embedding_service: SentenceTransformerEmbeddingService | None = None
_vector_store: FaissVectorStore | None = None


def answer_municipal_question(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, list[str] | str]:
    """Answer a municipal knowledge question using retrieved context.

    Args:
        question: User question about municipal services or policies.
        top_k: Number of document chunks to retrieve for grounding.

    Returns:
        A dictionary containing the grounded answer and source filenames.

    Raises:
        ValueError: If the question or retrieval settings are invalid.
        RuntimeError: If retrieval or Gemini response generation fails.
    """
    question_text = question.strip()
    if not question_text:
        raise ValueError("question cannot be empty.")

    retriever = _get_retriever()
    search_results = retriever.retrieve(question_text, top_k=top_k)

    if not search_results:
        return {
            "answer": (
                "I do not have enough official municipal information to "
                "answer that."
            ),
            "sources": [],
        }

    prompt = build_rag_prompt(question_text, search_results)
    answer = ask_gemini(prompt)

    return {
        "answer": answer,
        "sources": _extract_sources(search_results, answer),
    }


def _get_retriever() -> SemanticRetriever:
    """Return a semantic retriever backed by a ready FAISS vector store."""
    embedding_service = _get_embedding_service()
    vector_store = _get_vector_store(embedding_service)

    return SemanticRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


def _get_embedding_service() -> SentenceTransformerEmbeddingService:
    """Return a cached Sentence Transformers embedding service."""
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = SentenceTransformerEmbeddingService()

    return _embedding_service


def _get_vector_store(
    embedding_service: SentenceTransformerEmbeddingService,
) -> FaissVectorStore:
    """Return a cached FAISS vector store, loading or building as needed."""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    vector_store = FaissVectorStore()

    try:
        vector_store.load()
    except FileNotFoundError:
        documents = load_municipal_documents()
        chunks = chunk_documents(documents)
        embedded_documents = embedding_service.embed_documents(chunks)
        vector_store.build(embedded_documents)
        vector_store.save()

    _vector_store = vector_store
    return _vector_store


def _extract_sources(
    search_results: list[SearchResult],
    answer: str,
) -> list[str]:
    """Return source filenames cited in the answer.

    If the model does not include a recognizable source filename, fall back to
    the retrieved source list so callers still receive traceability metadata.
    """
    retrieved_sources = _extract_retrieved_sources(search_results)
    cited_sources = [
        source
        for source in retrieved_sources
        if re.search(rf"\b{re.escape(source)}\b", answer)
    ]

    return cited_sources or retrieved_sources


def _extract_retrieved_sources(search_results: list[SearchResult]) -> list[str]:
    """Return unique source filenames from retrieved chunks."""
    sources: list[str] = []

    for result in search_results:
        filename = result.document.metadata.get("filename")
        if filename and filename not in sources:
            sources.append(filename)

    return sources
