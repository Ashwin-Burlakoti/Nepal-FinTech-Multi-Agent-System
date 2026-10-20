"""RAG pipeline: ChromaDB storage, document ingestion, and multi-collection retrieval."""

from __future__ import annotations

from nepal_fintech.rag.ingest import (
    chunk_text,
    ingest_all_defaults,
    ingest_directory,
    ingest_file,
)
from nepal_fintech.rag.monitors import (
    LandPlanningMonitor,
    NepseFilingsMonitor,
    prune_expired_filings,
)
from nepal_fintech.rag.retriever import (
    multi_collection_retrieve,
    retrieve,
    retrieve_with_context,
)
from nepal_fintech.rag.store import ChromaStore, chroma_store

__all__ = [
    "ChromaStore",
    "LandPlanningMonitor",
    "NepseFilingsMonitor",
    "chroma_store",
    "chunk_text",
    "ingest_all_defaults",
    "ingest_directory",
    "ingest_file",
    "multi_collection_retrieve",
    "prune_expired_filings",
    "retrieve",
    "retrieve_with_context",
]
