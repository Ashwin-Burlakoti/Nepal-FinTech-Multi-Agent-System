"""FastAPI route handlers for users, agents, and notifications."""

from __future__ import annotations

from nepal_fintech.api.routes_agents import router as agents_router
from nepal_fintech.api.routes_notifications import router as notifications_router
from nepal_fintech.api.routes_user import router as user_router

__all__ = [
    "agents_router",
    "notifications_router",
    "user_router",
]
