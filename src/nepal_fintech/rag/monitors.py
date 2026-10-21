"""Live monitors and automated retention pruner for NEPSE and Land Planning."""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from nepal_fintech.rag.store import chroma_store

logger = logging.getLogger(__name__)


def _generate_doc_id(prefix: str, identifier: str, content: str) -> str:
    """Generate a stable deterministic ID for deduplicated ingestion."""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    safe_id = "".join(c if c.isalnum() else "_" for c in identifier)
    return f"{prefix}_{safe_id}_{digest}"


class NepseFilingsMonitor:
    """Monitors and continuously ingests NEPSE corporate filings and announcements."""

    def __init__(self, endpoint_url: str | None = None) -> None:
        self.endpoint_url = endpoint_url or "https://nepalstock.com.np/api/nots/announcement"

    async def fetch_and_ingest(self, client: httpx.AsyncClient | None = None) -> int:
        """Fetch latest filings from feed and upsert into ChromaDB nepse_filings."""
        logger.info("Checking for live NEPSE filings updates...")
        filings: list[dict[str, Any]] = []

        try:
            async with (client or httpx.AsyncClient(timeout=15.0)) as http:
                resp = await http.get(self.endpoint_url)
                if resp.status_code == 200:
                    data = resp.json()
                    # Handle both list responses and wrapped payload formats
                    items = data if isinstance(data, list) else data.get("data", [])
                    filings = items[:50]
        except Exception as exc:
            logger.warning("Could not reach NEPSE announcement feed (%s). Skipping live cycle.", exc)
            return 0

        if not filings:
            return 0

        docs: list[str] = []
        metadatas: list[dict[str, Any]] = []
        ids: list[str] = []
        current_year = datetime.now(UTC).year

        for item in filings:
            ticker = str(item.get("symbol") or item.get("company_code") or "GEN")
            title = str(item.get("title") or item.get("subject") or "NEPSE Notice")
            body = str(item.get("description") or item.get("content") or title)
            filing_date = str(item.get("date") or item.get("published_date") or "")
            filing_type = str(item.get("type") or item.get("category") or "disclosure")

            year = current_year
            if filing_date and len(filing_date) >= 4 and filing_date[:4].isdigit():
                year = int(filing_date[:4])

            doc_text = f"NEPSE Filing [{ticker}] - {title}\nDate: {filing_date}\nType: {filing_type}\n\n{body}"
            doc_id = _generate_doc_id("nepse", f"{ticker}_{filing_date}", doc_text)

            docs.append(doc_text)
            ids.append(doc_id)
            metadatas.append({
                "source": "nepse_filings",
                "ticker": ticker,
                "filing_type": filing_type,
                "filing_date": filing_date,
                "year": year,
                "ingested_at": datetime.now(UTC).isoformat(),
            })

        chroma_store.upsert_documents("nepse_filings", docs=docs, metadatas=metadatas, ids=ids)
        logger.info("Ingested/updated %d NEPSE filings into ChromaDB", len(docs))
        return len(docs)


class LandPlanningMonitor:
    """Monitors government urban planning, KVDA decisions, and land notices."""

    def __init__(self, endpoint_url: str | None = None) -> None:
        self.endpoint_url = endpoint_url or "https://kvda.gov.np/api/notices"

    async def fetch_and_ingest(self, client: httpx.AsyncClient | None = None) -> int:
        """Fetch latest town/land planning updates and upsert into kvda_plans."""
        logger.info("Checking for government land planning & KVDA updates...")
        notices: list[dict[str, Any]] = []

        try:
            async with (client or httpx.AsyncClient(timeout=15.0)) as http:
                resp = await http.get(self.endpoint_url)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get("notices", [])
                    notices = items[:50]
        except Exception as exc:
            logger.warning("Could not reach land planning feed (%s). Skipping live cycle.", exc)
            return 0

        if not notices:
            return 0

        docs: list[str] = []
        metadatas: list[dict[str, Any]] = []
        ids: list[str] = []
        current_year = datetime.now(UTC).year

        for item in notices:
            title = str(item.get("title") or "Urban Planning Notice")
            body = str(item.get("details") or item.get("summary") or title)
            authority = str(item.get("authority") or "KVDA / MoUD")
            region = str(item.get("region") or item.get("district") or "Kathmandu Valley")
            date_str = str(item.get("date") or "")

            year = current_year
            if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
                year = int(date_str[:4])

            doc_text = f"Land/Urban Planning: {title}\nAuthority: {authority}\nRegion: {region}\nDate: {date_str}\n\n{body}"
            doc_id = _generate_doc_id("kvda", f"{authority}_{region}_{date_str}", doc_text)

            docs.append(doc_text)
            ids.append(doc_id)
            metadatas.append({
                "source": "kvda_plans",
                "authority": authority,
                "region": region,
                "year": year,
                "ingested_at": datetime.now(UTC).isoformat(),
            })

        chroma_store.upsert_documents("kvda_plans", docs=docs, metadatas=metadatas, ids=ids)
        logger.info("Ingested/updated %d land planning notices into ChromaDB", len(docs))
        return len(docs)


def prune_expired_filings(max_age_years: int = 8) -> int:
    """Automatically prune filings older than max_age_years from ChromaDB.

    Filings older than 8-10 years are considered obsolete for active advisory.
    """
    current_year = datetime.now(UTC).year
    cutoff_year = current_year - max_age_years
    logger.info("Pruning NEPSE filings older than year %d (age > %d years)...", cutoff_year, max_age_years)

    deleted_count = chroma_store.delete_older_than("nepse_filings", cutoff_year=cutoff_year)
    logger.info("Pruned %d obsolete filings from nepse_filings", deleted_count)
    return deleted_count
