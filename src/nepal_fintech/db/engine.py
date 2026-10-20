"""Async SQLAlchemy engine setup and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from nepal_fintech.config import settings

from .models import Base

_url: str = f"sqlite+aiosqlite:///{settings.db_path}"

engine = create_async_engine(_url, echo=False, future=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables registered on ``Base.metadata``.

    Should be called once at application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closing it when done.

    Typical usage as a FastAPI / DI dependency::

        async for session in get_session():
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
