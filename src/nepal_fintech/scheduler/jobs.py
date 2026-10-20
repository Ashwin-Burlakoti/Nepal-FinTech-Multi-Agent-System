"""APScheduler jobs for periodic macro data refresh."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nepal_fintech.agents.market_analyzer import MarketAnalyzer
from nepal_fintech.db.crud import save_macro_state, save_notification
from nepal_fintech.db.engine import AsyncSessionLocal
from nepal_fintech.rag.monitors import (
    LandPlanningMonitor,
    NepseFilingsMonitor,
    prune_expired_filings,
)

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
nepse_monitor = NepseFilingsMonitor()
land_monitor = LandPlanningMonitor()


async def sync_nepse_filings() -> None:
    """Scheduled job: fetch live NEPSE filings and update ChromaDB."""
    try:
        count = await nepse_monitor.fetch_and_ingest()
        logger.info("NEPSE sync completed: %d filings processed", count)
    except Exception:
        logger.exception("NEPSE filings sync failed")


async def sync_land_planning() -> None:
    """Scheduled job: fetch government land/town planning announcements."""
    try:
        count = await land_monitor.fetch_and_ingest()
        logger.info("Land planning sync completed: %d notices processed", count)
    except Exception:
        logger.exception("Land planning sync failed")


def prune_stale_filings_job() -> None:
    """Scheduled job: automatically prune filings older than 8 years."""
    try:
        pruned = prune_expired_filings(max_age_years=8)
        logger.info("Filings retention cleanup finished: %d obsolete filings removed", pruned)
    except Exception:
        logger.exception("Filings retention cleanup failed")


async def refresh_macro_state() -> None:
    """Run MarketAnalyzer and cache the updated macro state."""
    logger.info("Scheduled macro refresh starting...")
    agent = MarketAnalyzer()
    context = {
        "global_data": "Fetch latest global macro indicators",
        "nepal_data": "Fetch latest Nepal economic data",
        "news": "Latest market-moving news",
    }
    try:
        payload = await agent.run(context)
        async with AsyncSessionLocal() as session:
            await save_macro_state(session, payload.model_dump_json())
            # Save notification for the first active user if one exists
            from sqlalchemy import select
            from nepal_fintech.db.models import User
            first_user = (await session.execute(select(User.id).limit(1))).scalar_one_or_none()
            if first_user is not None:
                await save_notification(session, user_id=first_user, payload=payload)
        logger.info("Macro state refreshed successfully")
    except Exception:
        logger.exception("Macro refresh failed")


def start_scheduler() -> None:
    """Start the APScheduler with periodic macro, live filings, land planning, and retention jobs."""
    scheduler.add_job(
        refresh_macro_state,
        "interval",
        hours=6,
        id="macro_refresh",
        replace_existing=True,
    )
    scheduler.add_job(
        sync_nepse_filings,
        "interval",
        hours=2,
        id="nepse_sync",
        replace_existing=True,
    )
    scheduler.add_job(
        sync_land_planning,
        "interval",
        hours=6,
        id="land_planning_sync",
        replace_existing=True,
    )
    scheduler.add_job(
        prune_stale_filings_job,
        "interval",
        hours=24,
        id="filings_retention_prune",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started with periodic jobs: macro(6h), NEPSE(2h), land(6h), retention(24h)")


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
