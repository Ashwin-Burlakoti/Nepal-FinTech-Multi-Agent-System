"""RAG retriever — query ChromaDB and format context for LLM prompts."""

from __future__ import annotations

from nepal_fintech.rag.store import COLLECTIONS, chroma_store


def retrieve(
    query: str,
    collection_name: str = "tax_acts",
    n_results: int = 5,
) -> list[dict]:
    """Query ChromaDB and return structured results."""
    raw = chroma_store.query(collection_name, query, n_results=n_results)
    results: list[dict] = []
    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]
    for doc, meta, dist in zip(documents, metadatas, distances):
        results.append({"text": doc, "metadata": meta, "distance": dist})
    return results


def retrieve_with_context(
    query: str,
    collection_name: str = "tax_acts",
    n_results: int = 5,
) -> str:
    """Query ChromaDB and format results into an LLM-ready context string."""
    results = retrieve(query, collection_name, n_results)
    if not results:
        return "No relevant documents found in the knowledge base."
    parts: list[str] = []
    for i, r in enumerate(results, 1):
        source = r["metadata"].get("source", "unknown")
        chunk_idx = r["metadata"].get("chunk_index", "?")
        parts.append(
            f"[Source {i}: {source}, chunk {chunk_idx}]\n{r['text']}\n"
        )
    return "\n---\n".join(parts)


def multi_collection_retrieve(
    query: str,
    collections: list[str] | None = None,
    n_results: int = 3,
) -> str:
    """Query multiple ChromaDB collections and merge into context string."""
    target_collections = collections or list(COLLECTIONS.keys())
    all_parts: list[str] = []
    for coll_name in target_collections:
        try:
            context = retrieve_with_context(query, coll_name, n_results)
            if "No relevant documents" not in context:
                all_parts.append(f"== {coll_name.upper()} ==\n{context}")
        except Exception:  # noqa: BLE001
            continue
    if not all_parts:
        return "No relevant documents found across any collection."
    return "\n\n".join(all_parts)
