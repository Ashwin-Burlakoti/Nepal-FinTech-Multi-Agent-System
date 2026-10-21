"""FastAPI application factory with lifespan management."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from nepal_fintech.config import settings
from nepal_fintech.db.engine import init_db
from nepal_fintech.scheduler.jobs import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup: init DB, bootstrap RAG if needed, and start scheduler."""
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Initializing database...")
    await init_db()

    logger.info("Checking RAG knowledge collections...")
    from nepal_fintech.rag.ingest import ingest_all_defaults
    from nepal_fintech.rag.store import chroma_store

    try:
        if chroma_store.count("tax_acts") == 0:
            logger.info("Bootstrapping default tax acts into ChromaDB...")
            ingest_all_defaults()
    except Exception as exc:
        logger.warning("RAG bootstrap note: %s", exc)

    logger.info("Starting scheduler...")
    start_scheduler()
    yield
    logger.info("Shutting down scheduler...")
    stop_scheduler()


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="Nepal FinTech AI Advisory",
        description="AI-powered Wealth & Tax Advisory for Nepal",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Register routers
    from nepal_fintech.api.routes_agents import router as agents_router
    from nepal_fintech.api.routes_notifications import router as notif_router
    from nepal_fintech.api.routes_user import router as user_router

    app.include_router(user_router)
    app.include_router(agents_router)
    app.include_router(notif_router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


def cli_main() -> None:
    """CLI entry point for nepal-fintech (api, ui, or all)."""
    import argparse
    import threading

    import uvicorn

    from nepal_fintech.ui.app import start_ui

    parser = argparse.ArgumentParser(description="Nepal FinTech AI Advisory System")
    parser.add_argument(
        "mode",
        nargs="?",
        default="api",
        choices=["api", "ui", "all"],
        help="Run mode: api (default FastAPI server), ui (Flet interface), or all (both)",
    )
    args = parser.parse_args()

    if args.mode == "ui":
        start_ui()
    elif args.mode == "api":
        uvicorn.run(
            "nepal_fintech.main:app",
            host=settings.app_host,
            port=settings.app_port,
            reload=settings.debug,
        )
    elif args.mode == "all":
        server_thread = threading.Thread(
            target=uvicorn.run,
            args=("nepal_fintech.main:app",),
            kwargs={"host": settings.app_host, "port": settings.app_port, "log_level": "info"},
            daemon=True,
        )
        server_thread.start()
        start_ui()
