"""Document ingestion pipeline for the RAG module."""

from __future__ import annotations

from pathlib import Path

from nepal_fintech.rag.store import chroma_store

# Default directory where raw documents live.
_DEFAULT_RAG_DOCS_DIR: Path = (
    Path(__file__).resolve().parents[3] / "data" / "rag_docs"
)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split *text* into overlapping chunks.

    Args:
        text: The full document text.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not text:
        return []

    chunks: list[str] = []
    start: int = 0
    text_len: int = len(text)

    while start < text_len:
        end: int = start + chunk_size
        chunks.append(text[start:end])
        # Advance by (chunk_size - overlap) to create overlap
        start += chunk_size - overlap

    return chunks


def ingest_file(file_path: Path, collection_name: str) -> int:
    """Read a text file, chunk it, and add it to ChromaDB.

    Args:
        file_path: Path to the ``.txt`` file to ingest.
        collection_name: Target ChromaDB collection.

    Returns:
        The number of chunks added.
    """
    text: str = file_path.read_text(encoding="utf-8")
    chunks: list[str] = chunk_text(text)

    if not chunks:
        return 0

    stem: str = file_path.stem
    ids: list[str] = [f"{stem}_chunk_{i}" for i in range(len(chunks))]
    metadatas: list[dict[str, str | int]] = [
        {"source": file_path.name, "chunk_index": i}
        for i in range(len(chunks))
    ]

    chroma_store.add_documents(
        collection_name=collection_name,
        docs=chunks,
        metadatas=metadatas,  # type: ignore[arg-type]
        ids=ids,
    )
    return len(chunks)


def ingest_directory(dir_path: Path, collection_name: str) -> int:
    """Ingest all ``.txt`` files in a directory into a ChromaDB collection.

    Args:
        dir_path: Directory containing ``.txt`` files.
        collection_name: Target ChromaDB collection.

    Returns:
        Total number of chunks ingested across all files.
    """
    total: int = 0
    for txt_file in sorted(dir_path.glob("*.txt")):
        total += ingest_file(txt_file, collection_name)
    return total


def ingest_all_defaults() -> dict[str, int]:
    """Ingest documents from the default ``data/rag_docs/`` directory.

    Currently ingests all ``.txt`` files into the ``tax_acts`` collection.

    Returns:
        A dict mapping collection name to the number of chunks ingested.
    """
    results: dict[str, int] = {}

    if _DEFAULT_RAG_DOCS_DIR.is_dir():
        results["tax_acts"] = ingest_directory(
            _DEFAULT_RAG_DOCS_DIR, "tax_acts"
        )
    else:
        results["tax_acts"] = 0

    return results
