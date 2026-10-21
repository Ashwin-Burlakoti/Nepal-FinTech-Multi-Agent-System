"""Async CRUD operations for users, notifications, and macro state."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nepal_fintech.db.models import MacroStateRecord, Notification, User
from nepal_fintech.encryption import decrypt, encrypt
from nepal_fintech.engine.schemas import NotificationPayload, UserProfile


async def create_user(session: AsyncSession, profile: UserProfile) -> int:
    """Create a user with encrypted financial fields. Returns user ID."""
    user = User(
        name=profile.name,
        email=profile.email,
        income_sources=encrypt(
            json.dumps([s.model_dump() for s in profile.income_sources])
        ),
        portfolio_split=encrypt(profile.portfolio_split.model_dump_json()),
        risk_profile=profile.risk_profile,
        created_at=datetime.now(UTC),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user.id


async def get_user(session: AsyncSession, user_id: int) -> dict | None:
    """Retrieve and decrypt a user profile by ID."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "income_sources": json.loads(decrypt(user.income_sources)),
        "portfolio_split": json.loads(decrypt(user.portfolio_split)),
        "risk_profile": user.risk_profile,
        "created_at": user.created_at.isoformat(),
    }


async def save_notification(
    session: AsyncSession, user_id: int, payload: NotificationPayload
) -> int:
    """Save a triad notification to the database. Returns notification ID."""
    notif = Notification(
        user_id=user_id,
        agent_type=payload.agent_type,
        short_title=payload.short_title,
        action_summary=payload.action_summary,
        thinker_points=json.dumps(payload.thinker_output.model_dump()),
        critique_risks=json.dumps(payload.critique_output.model_dump()),
        judge_verdict=payload.judge_verdict.decision,
        citations=json.dumps(payload.judge_verdict.citations),
        is_read=False,
        created_at=datetime.now(UTC),
    )
    session.add(notif)
    await session.commit()
    await session.refresh(notif)
    return notif.id


async def get_notifications(
    session: AsyncSession, user_id: int, *, unread_only: bool = False
) -> list[dict]:
    """List notifications for a user, optionally filtered to unread."""
    stmt = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)
    stmt = stmt.order_by(Notification.created_at.desc())
    result = await session.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "id": n.id,
            "agent_type": n.agent_type,
            "short_title": n.short_title,
            "action_summary": n.action_summary,
            "thinker_points": json.loads(n.thinker_points),
            "critique_risks": json.loads(n.critique_risks),
            "judge_verdict": n.judge_verdict,
            "citations": json.loads(n.citations),
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in rows
    ]


async def mark_notification_read(
    session: AsyncSession, notification_id: int
) -> None:
    """Mark a single notification as read."""
    result = await session.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        msg = f"Notification {notification_id} not found"
        raise ValueError(msg)
    notif.is_read = True
    await session.commit()


async def save_macro_state(session: AsyncSession, state_json: str) -> int:
    """Cache a MarketAnalyzer macro state snapshot. Returns record ID."""
    record = MacroStateRecord(
        snapshot=state_json,
        created_at=datetime.now(UTC),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record.id


async def get_latest_macro_state(session: AsyncSession) -> str | None:
    """Retrieve the most recent cached macro state JSON."""
    stmt = (
        select(MacroStateRecord)
        .order_by(MacroStateRecord.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    record = result.scalar_one_or_none()
    return record.snapshot if record else None
