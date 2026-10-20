"""Notification API routes — list, read, mark-as-read."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nepal_fintech.db.crud import (
    get_notifications,
    mark_notification_read,
)
from nepal_fintech.db.engine import get_session

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(
    user_id: int = 1,
    unread_only: bool = False,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """List notifications for a user, optionally filtered to unread."""
    return await get_notifications(session, user_id, unread_only=unread_only)


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Mark a notification as read."""
    try:
        await mark_notification_read(session, notification_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Notification marked as read"}
