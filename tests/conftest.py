"""Pytest fixtures for Nepal FinTech testing."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set required test environment variables before importing app modules
test_key = Fernet.generate_key().decode()
os.environ["ENCRYPTION_KEY"] = test_key
os.environ["DB_PATH"] = ":memory:"
os.environ["CHROMA_PERSIST_DIR"] = ".test_chroma"
os.environ["LLM_API_KEY"] = "test-key"

from nepal_fintech.db.models import Base

# Test async SQLite in-memory engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    future=True,
)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an active async database session against an in-memory schema."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
