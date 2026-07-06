"""Document loading utilities for the CityPulse RAG pipeline."""

from pathlib import Path

from langchain_core.documents import Document


MUNICIPAL_DOCS_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "municipal_docs"
)


def load_municipal_documents(
    directory: Path = MUNICIPAL_DOCS_DIR,
) -> list[Document]:
    """Load municipal TXT documents as LangChain ``Document`` objects.

    Args:
        directory: Directory containing municipal knowledge base ``.txt``
            files. Defaults to the project's bundled municipal documents.

    Returns:
        A list of LangChain ``Document`` objects, each containing the file
        contents and metadata with the source filename.

    Raises:
        FileNotFoundError: If the configured municipal documents directory
            does not exist.
        NotADirectoryError: If the configured path exists but is not a
            directory.
    """
    docs_dir = Path(directory)

    if not docs_dir.exists():
        raise FileNotFoundError(
            f"Municipal documents directory does not exist: {docs_dir}"
        )

    if not docs_dir.is_dir():
        raise NotADirectoryError(
            f"Municipal documents path is not a directory: {docs_dir}"
        )

    documents: list[Document] = []

    for file_path in sorted(docs_dir.glob("*.txt")):
        documents.append(
            Document(
                page_content=file_path.read_text(encoding="utf-8"),
                metadata={"filename": file_path.name},
            )
        )

    return documents
