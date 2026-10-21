"""SQLAlchemy 2.0 ORM models for the Nepal FinTech database."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class User(Base):
    """Registered user with encrypted financial profile data."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    income_sources: Mapped[str] = mapped_column(String, nullable=False, doc="Encrypted JSON")
    portfolio_split: Mapped[str] = mapped_column(String, nullable=False, doc="Encrypted JSON")
    risk_profile: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False,
    )


class Notification(Base):
    """Agent-generated notification delivered to a user."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False,
    )
    agent_type: Mapped[str] = mapped_column(String, nullable=False)
    short_title: Mapped[str] = mapped_column(String(60), nullable=False)
    action_summary: Mapped[str] = mapped_column(String, nullable=False)
    thinker_points: Mapped[str] = mapped_column(String, nullable=False, doc="JSON")
    critique_risks: Mapped[str] = mapped_column(String, nullable=False, doc="JSON")
    judge_verdict: Mapped[str] = mapped_column(String, nullable=False)
    citations: Mapped[str] = mapped_column(String, nullable=False, doc="JSON")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False,
    )


class MacroStateRecord(Base):
    """Point-in-time snapshot of macroeconomic state."""

    __tablename__ = "macro_state_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot: Mapped[str] = mapped_column(String, nullable=False, doc="Full JSON")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False,
    )
