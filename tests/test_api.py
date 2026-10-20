"""Tests for FastAPI endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from nepal_fintech.db.engine import get_session
from nepal_fintech.main import app


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Async test client with database dependency override."""
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_user_onboard_and_get_profile(client: AsyncClient) -> None:
    payload = {
        "name": "Pradeep Giri",
        "email": "pradeep@nepalinvest.com",
        "income_sources": [
            {
                "source_type": "salary",
                "annual_amount_npr": 1800000,
                "description": "Tech Lead",
            }
        ],
        "portfolio_split": {
            "land_pct": 50,
            "shares_pct": 30,
            "cash_pct": 20,
        },
        "risk_profile": "moderate",
    }
    # Onboard user
    resp = await client.post("/api/users/onboard", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "user_id" in data
    user_id = data["user_id"]

    # Fetch profile
    profile_resp = await client.get(f"/api/users/profile/{user_id}")
    assert profile_resp.status_code == 200
    pdata = profile_resp.json()
    assert pdata["name"] == "Pradeep Giri"
    assert pdata["email"] == "pradeep@nepalinvest.com"


@pytest.mark.asyncio
async def test_notifications_endpoint(client: AsyncClient) -> None:
    resp = await client.get("/api/notifications/", params={"user_id": 1})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_macro_latest_not_found(client: AsyncClient) -> None:
    resp = await client.get("/api/agents/macro/latest")
    assert resp.status_code in (404, 200)
