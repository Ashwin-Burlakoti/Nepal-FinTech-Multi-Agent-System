"""User onboarding and profile API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nepal_fintech.db.crud import create_user, get_user
from nepal_fintech.db.engine import get_session
from nepal_fintech.engine.schemas import UserProfile

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/onboard", status_code=201)
async def onboard_user(
    profile: UserProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Create a new user with encrypted financial data."""
    user_id = await create_user(session, profile)
    return {"user_id": user_id, "message": "User onboarded successfully"}


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Retrieve a user profile (decrypted)."""
    user = await get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
