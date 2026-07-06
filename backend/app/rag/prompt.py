"""Prompt builders for grounded CityPulse RAG answers."""

from langchain_core.documents import Document

from app.rag.vector_store import SearchResult


def build_context(search_results: list[SearchResult]) -> str:
    """Build source-labeled context from retrieved document chunks.

    Args:
        search_results: Ranked document chunks returned by semantic retrieval.

    Returns:
        A context string with source filenames attached to each chunk.

    Raises:
        ValueError: If no retrieved chunks are provided.
    """
    if not search_results:
        raise ValueError("search_results cannot be empty.")

    context_blocks = [
        _format_context_block(index=index, document=result.document)
        for index, result in enumerate(search_results, start=1)
    ]

    return "\n\n".join(context_blocks)


def build_rag_prompt(question: str, search_results: list[SearchResult]) -> str:
    """Create a grounded RAG prompt for Gemini.

    Args:
        question: Citizen or municipal staff question.
        search_results: Retrieved municipal knowledge chunks.

    Returns:
        A prompt instructing the model to answer only from supplied context and
        cite source filenames.

    Raises:
        ValueError: If the question or retrieved context is empty.
    """
    question_text = question.strip()
    if not question_text:
        raise ValueError("question cannot be empty.")

    context = build_context(search_results)

    return f"""You are the CityPulse AI municipal knowledge assistant.

Answer the question using ONLY the official municipal context below.

Rules:
- Do not use outside knowledge.
- If the answer is not in the context, say: "I do not have enough official municipal information to answer that."
- Be concise and practical.
- Include a "Sources" line listing the source filename(s) used.
- Do not invent policy details, schedules, departments, ward numbers, or timelines.

Context:
{context}

Question:
{question_text}

Answer:"""


def _format_context_block(index: int, document: Document) -> str:
    """Format one retrieved document chunk for prompt context."""
    filename = document.metadata.get("filename", "unknown_source")
    content = document.page_content.strip()

    if not content:
        raise ValueError(f"Retrieved document '{filename}' has empty content.")

    return f"[Source {index}: {filename}]\n{content}"
