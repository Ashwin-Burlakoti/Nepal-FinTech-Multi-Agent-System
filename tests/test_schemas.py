"""Tests for Pydantic schemas and validation rules."""

from __future__ import annotations

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from nepal_fintech.engine.schemas import (
    GlobalMacro,
    IncomeSource,
    JudgeVerdict,
    MacroState,
    NepalLocal,
    NotificationPayload,
    PortfolioSplit,
    ThinkerOutput,
    CritiqueOutput,
    UserProfile,
)


def test_portfolio_split_valid() -> None:
    split = PortfolioSplit(land_pct=50, shares_pct=30, cash_pct=20)
    assert split.land_pct == 50
    assert split.shares_pct == 30
    assert split.cash_pct == 20


def test_portfolio_split_invalid_sum() -> None:
    with pytest.raises(ValidationError):
        PortfolioSplit(land_pct=60, shares_pct=30, cash_pct=20)  # sums to 110


def test_portfolio_split_negative() -> None:
    with pytest.raises(ValidationError):
        PortfolioSplit(land_pct=-10, shares_pct=60, cash_pct=50)


def test_user_profile_valid() -> None:
    profile = UserProfile(
        name="Aarav Sharma",
        email="aarav@example.com",
        income_sources=[
            IncomeSource(source_type="salary", annual_amount_npr=1200000, description="Software Eng")
        ],
        portfolio_split=PortfolioSplit(land_pct=70, shares_pct=20, cash_pct=10),
        risk_profile="moderate",
    )
    assert profile.name == "Aarav Sharma"
    assert len(profile.income_sources) == 1


def test_judge_verdict_requires_citations() -> None:
    with pytest.raises(ValidationError):
        JudgeVerdict(
            decision="Buy hydropower shares",
            confidence="high",
            action_items=["Buy 100 units"],
            citations=[],  # Empty citations must be rejected
        )


def test_judge_verdict_valid() -> None:
    verdict = JudgeVerdict(
        decision="Restructure salary via Section 12",
        confidence="high",
        action_items=["Contribute NPR 300,000 to CIT"],
        citations=["Income Tax Act 2058, Section 12"],
    )
    assert verdict.confidence == "high"
    assert len(verdict.citations) == 1


def test_macro_state_schema() -> None:
    macro = MacroState(
        global_macro=GlobalMacro(
            us_m2_trend="Expanding",
            us_bond_yields="4.2%",
            japan_policy="Neutral",
            china_policy="Stimulus",
            india_policy="RBI repo 6.5%",
            nasdaq="Bullish",
            nikkei="Steady",
            sgx="Stable",
            oil_gold_energy="Brent $78",
            defense_ai_sector="High CapEx",
            geopolitical_risks="Moderate",
        ),
        nepal_local=NepalLocal(
            gdp_trend="4.5%",
            nepse_status="Consolidating",
            nrb_policy="Accommodative",
            kvda_updates="Land pooling notices",
            land_price_trend="Upward in outskirts",
        ),
        spillover_analysis="Remittance inflow cushions NPR liquidity",
        timestamp=datetime.now(timezone.utc),
    )
    assert macro.nepal_local.gdp_trend == "4.5%"
    assert "Remittance" in macro.spillover_analysis
