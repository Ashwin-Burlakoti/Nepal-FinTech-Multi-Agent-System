"""Tests for ChromaDB store, ingestion, retrieval, and retention pruning."""

from __future__ import annotations

from nepal_fintech.rag.ingest import chunk_text
from nepal_fintech.rag.monitors import prune_expired_filings
from nepal_fintech.rag.retriever import retrieve_with_context
from nepal_fintech.rag.store import ChromaStore


def test_chunk_text_basic() -> None:
    text = "A" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 3
    assert len(chunks[0]) == 500


def test_chunk_text_empty() -> None:
    assert chunk_text("") == []


def test_chroma_store_upsert_and_query() -> None:
    store = ChromaStore()
    docs = ["Nepal Income Tax Section 10 covers natural persons."]
    metas = [{"source": "test_act", "year": 2024}]
    ids = ["test_doc_1"]

    store.upsert_documents("tax_acts", docs=docs, metadatas=metas, ids=ids)
    assert store.count("tax_acts") >= 1

    res = store.query("tax_acts", "Section 10 natural persons", n_results=1)
    assert len(res["documents"][0]) >= 1
    assert "Section 10" in res["documents"][0][0]


def test_retriever_context_format() -> None:
    ctx = retrieve_with_context("Section 10", collection_name="tax_acts", n_results=1)
    assert isinstance(ctx, str)
    assert len(ctx) > 0


def test_retention_pruning() -> None:
    store = ChromaStore()
    # Insert older filing (e.g. 2012, > 8 years old) and recent filing (2024)
    docs = [
        "Old filing from 2012 regarding AGM notice",
        "Recent filing from 2024 dividend declaration",
    ]
    metas = [
        {"source": "nepse", "ticker": "NABIL", "year": 2012},
        {"source": "nepse", "ticker": "NABIL", "year": 2024},
    ]
    ids = ["filing_old_2012", "filing_recent_2024"]

    store.upsert_documents("nepse_filings", docs=docs, metadatas=metas, ids=ids)

    # Prune filings older than 8 years
    pruned = prune_expired_filings(max_age_years=8)
    assert pruned >= 1

    # Verify recent document remains
    col = store.get_collection("nepse_filings")
    recent = col.get(ids=["filing_recent_2024"])
    assert len(recent["ids"]) == 1
