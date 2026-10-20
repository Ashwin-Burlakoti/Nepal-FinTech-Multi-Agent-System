"""Tests for live NEPSE and government Land Planning monitors."""

from __future__ import annotations

import httpx
import pytest

from nepal_fintech.rag.monitors import (
    LandPlanningMonitor,
    NepseFilingsMonitor,
    _generate_doc_id,
)
from nepal_fintech.rag.store import chroma_store


def test_generate_doc_id_deterministic() -> None:
    id1 = _generate_doc_id("nepse", "NABIL_2024", "Dividend announcement")
    id2 = _generate_doc_id("nepse", "NABIL_2024", "Dividend announcement")
    assert id1 == id2
    assert id1.startswith("nepse_NABIL_2024_")


@pytest.mark.asyncio
async def test_nepse_monitor_with_mock_client() -> None:
    # Mock transport simulating NEPSE announcement API
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=[
                {
                    "symbol": "CHCL",
                    "title": "Chilime Hydropower 15% Bonus Share Proposed",
                    "description": "BoD proposed 10% bonus share and 5% cash dividend for FY 2080/81.",
                    "date": "2024-10-15",
                    "type": "dividend",
                }
            ],
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    monitor = NepseFilingsMonitor(endpoint_url="https://mock.nepse/api")

    count = await monitor.fetch_and_ingest(client=mock_client)
    assert count == 1

    # Verify query in ChromaDB
    res = chroma_store.query("nepse_filings", "Chilime Hydropower bonus share", n_results=1)
    assert len(res["documents"][0]) >= 1
    assert "CHCL" in res["documents"][0][0]


@pytest.mark.asyncio
async def test_land_planning_monitor_with_mock_client() -> None:
    # Mock transport simulating government town planning notice feed
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "notices": [
                    {
                        "title": "Land Pooling and Infrastructure Gazette",
                        "details": "Government notification on 8-meter road setback and land pooling allocation.",
                        "authority": "KVDA",
                        "region": "Lalitpur",
                        "date": "2024-09-20",
                    }
                ]
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    monitor = LandPlanningMonitor(endpoint_url="https://mock.gov.np/api")

    count = await monitor.fetch_and_ingest(client=mock_client)
    assert count == 1

    # Verify query in ChromaDB
    res = chroma_store.query("kvda_plans", "Land Pooling setback", n_results=1)
    assert len(res["documents"][0]) >= 1
    assert "KVDA" in res["documents"][0][0]
