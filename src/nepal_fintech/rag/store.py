"""ChromaDB collection manager for the RAG module."""

from __future__ import annotations

from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from nepal_fintech.config import settings

COLLECTIONS: dict[str, str] = {
    "tax_acts": "Nepal Tax Acts and regulations",
    "kvda_plans": "KVDA town planning documents",
    "nepse_filings": "NEPSE company filings and reports",
}


class ChromaStore:
    """Manages ChromaDB persistent collections for document storage and retrieval."""

    def __init__(self) -> None:
        """Initialise the persistent ChromaDB client."""
        self._client: chromadb.ClientAPI = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
        )

    def get_collection(self, name: str) -> Collection:
        """Get or create a ChromaDB collection by name.

        Args:
            name: The collection name. Should be a key in :data:`COLLECTIONS`.

        Returns:
            The ChromaDB ``Collection`` instance.
        """
        metadata: dict[str, str] | None = None
        if name in COLLECTIONS:
            metadata = {"description": COLLECTIONS[name]}
        return self._client.get_or_create_collection(
            name=name,
            metadata=metadata,
        )

    def add_documents(
        self,
        collection_name: str,
        docs: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Add documents to a ChromaDB collection."""
        collection: Collection = self.get_collection(collection_name)
        collection.add(documents=docs, metadatas=metadatas, ids=ids)

    def upsert_documents(
        self,
        collection_name: str,
        docs: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Upsert documents into collection, avoiding duplicate ID errors."""
        collection: Collection = self.get_collection(collection_name)
        collection.upsert(documents=docs, metadatas=metadatas, ids=ids)

    def count(self, collection_name: str) -> int:
        """Return the number of documents in a collection."""
        collection: Collection = self.get_collection(collection_name)
        return collection.count()

    def delete_older_than(self, collection_name: str, cutoff_year: int) -> int:
        """Prune documents with year < cutoff_year. Returns number deleted."""
        collection: Collection = self.get_collection(collection_name)
        existing = collection.get(where={"year": {"$lt": cutoff_year}})
        ids_to_delete = existing.get("ids", [])
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
    ) -> dict[str, list]:
        """Query a collection with a text string.

        Args:
            collection_name: The collection to search.
            query_text: The natural-language query.
            n_results: Maximum number of results to return.

        Returns:
            Raw ChromaDB query results dict containing documents, metadatas,
            distances, and ids.
        """
        collection: Collection = self.get_collection(collection_name)
        results: dict[str, list] = collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        return results


# Module-level singleton
chroma_store: ChromaStore = ChromaStore()
