"""Tests for async SQLite models and CRUD operations."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nepal_fintech.db.crud import (
    create_user,
    get_latest_macro_state,
    get_notifications,
    get_user,
    mark_notification_read,
    save_macro_state,
    save_notification,
)
from nepal_fintech.db.models import User
from nepal_fintech.engine.schemas import (
    CritiqueOutput,
    IncomeSource,
    JudgeVerdict,
    NotificationPayload,
    PortfolioSplit,
    ThinkerOutput,
    UserProfile,
)


@pytest.mark.asyncio
async def test_create_and_get_user(db_session: AsyncSession) -> None:
    profile = UserProfile(
        name="Bijay Thapa",
        email="bijay@nepalfintech.io",
        income_sources=[
            IncomeSource(source_type="salary", annual_amount_npr=1500000, description="Salary"),
            IncomeSource(source_type="rental", annual_amount_npr=400000, description="Flat rent"),
        ],
        portfolio_split=PortfolioSplit(land_pct=60, shares_pct=25, cash_pct=15),
        risk_profile="moderate",
    )

    user_id = await create_user(db_session, profile)
    assert user_id > 0

    # Verify directly in SQLite that income_sources is encrypted (not raw JSON)
    raw_user = (await db_session.execute(select(User).where(User.id == user_id))).scalar_one()
    assert "1500000" not in raw_user.income_sources
    assert "salary" not in raw_user.income_sources

    # Verify get_user decrypts correctly
    user_dict = await get_user(db_session, user_id)
    assert user_dict is not None
    assert user_dict["name"] == "Bijay Thapa"
    assert len(user_dict["income_sources"]) == 2
    assert user_dict["portfolio_split"]["land_pct"] == 60


@pytest.mark.asyncio
async def test_notification_flow(db_session: AsyncSession) -> None:
    # First create a user
    profile = UserProfile(
        name="Sunita KC",
        email="sunita@example.com",
        income_sources=[
            IncomeSource(source_type="business", annual_amount_npr=2000000, description="Export firm")
        ],
        portfolio_split=PortfolioSplit(land_pct=40, shares_pct=40, cash_pct=20),
        risk_profile="aggressive",
    )
    user_id = await create_user(db_session, profile)

    payload = NotificationPayload(
        agent_type="tax_planner",
        short_title="Utilize Section 12 Retirement Deductions",
        action_summary="Deposit NPR 300,000 into Social Security Fund",
        thinker_output=ThinkerOutput(
            thesis="Section 12 provides NPR 300,000 deductible allowance",
            key_points=["Reduce taxable bracket", "Immediate cash benefit"],
            data_sources=["Income Tax Act 2058, Section 12"],
        ),
        critique_output=CritiqueOutput(
            objections=["Requires approved fund verification"],
            risk_flags=["Documentation audit"],
            compliance_issues=[],
        ),
        judge_verdict=JudgeVerdict(
            decision="Deposit NPR 300,000 to SSF immediately",
            confidence="high",
            action_items=["Obtain SSF deposit slip"],
            citations=["Income Tax Act 2058, Section 12, Clause 1"],
        ),
    )

    notif_id = await save_notification(db_session, user_id, payload)
    assert notif_id > 0

    # Retrieve notifications
    all_notifs = await get_notifications(db_session, user_id)
    assert len(all_notifs) == 1
    assert all_notifs[0]["is_read"] is False
    assert all_notifs[0]["agent_type"] == "tax_planner"

    # Mark as read
    await mark_notification_read(db_session, notif_id)
    unread_notifs = await get_notifications(db_session, user_id, unread_only=True)
    assert len(unread_notifs) == 0


@pytest.mark.asyncio
async def test_macro_state_cache(db_session: AsyncSession) -> None:
    snapshot = '{"spillover_analysis": "Fed rate pause supports NEPSE liquidity"}'
    rec_id = await save_macro_state(db_session, snapshot)
    assert rec_id > 0

    retrieved = await get_latest_macro_state(db_session)
    assert retrieved is not None
    assert "Fed rate pause" in retrieved
