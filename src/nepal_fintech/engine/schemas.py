"""Shared Pydantic schemas for the Nepal FinTech Multi-Agent System."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator

# ── User I/O ──────────────────────────────────────────────────────────


class IncomeSource(BaseModel):
    """Single income source with type and annual amount in NPR."""

    source_type: Literal[
        "salary", "business", "rental", "capital_gains", "other"
    ]
    annual_amount_npr: float = Field(gt=0)
    description: str


class PortfolioSplit(BaseModel):
    """Portfolio allocation percentages — must sum to 100."""

    land_pct: float = Field(ge=0, le=100)
    shares_pct: float = Field(ge=0, le=100)
    cash_pct: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def _check_sum(self) -> PortfolioSplit:
        total = self.land_pct + self.shares_pct + self.cash_pct
        if abs(total - 100.0) > 0.01:
            msg = f"Portfolio split must sum to 100, got {total}"
            raise ValueError(msg)
        return self


class UserProfile(BaseModel):
    """Complete user onboarding profile."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    income_sources: list[IncomeSource] = Field(min_length=1)
    portfolio_split: PortfolioSplit
    risk_profile: Literal["conservative", "moderate", "aggressive"]


# ── Triad Engine I/O ──────────────────────────────────────────────────


class ThinkerOutput(BaseModel):
    """Strategic thesis produced by the Thinker step."""

    thesis: str
    key_points: list[str] = Field(min_length=1)
    data_sources: list[str]


class CritiqueOutput(BaseModel):
    """Red-team analysis from the Critique step."""

    objections: list[str]
    risk_flags: list[str]
    compliance_issues: list[str]


class JudgeVerdict(BaseModel):
    """Final synthesized decision — citations are REQUIRED."""

    decision: str
    confidence: Literal["low", "medium", "high"]
    action_items: list[str]
    citations: list[str] = Field(min_length=1)


class NotificationPayload(BaseModel):
    """Full notification emitted by every agent after the triad pipeline."""

    agent_type: str
    short_title: str = Field(max_length=60)
    action_summary: str
    thinker_output: ThinkerOutput
    critique_output: CritiqueOutput
    judge_verdict: JudgeVerdict


# ── MarketAnalyzer ────────────────────────────────────────────────────


class GlobalMacro(BaseModel):
    """Global macroeconomic indicators snapshot."""

    us_m2_trend: str
    us_bond_yields: str
    japan_policy: str
    china_policy: str
    india_policy: str
    nasdaq: str
    nikkei: str
    sgx: str
    oil_gold_energy: str
    defense_ai_sector: str
    geopolitical_risks: str


class NepalLocal(BaseModel):
    """Nepal-specific economic and market indicators."""

    gdp_trend: str
    nepse_status: str
    nrb_policy: str
    kvda_updates: str
    land_price_trend: str


class MacroState(BaseModel):
    """Combined global + Nepal macro state with spillover analysis."""

    global_macro: GlobalMacro
    nepal_local: NepalLocal
    spillover_analysis: str
    timestamp: datetime


# ── Agent-Specific Outputs ────────────────────────────────────────────


class TaxSuggestion(BaseModel):
    """Single tax-saving strategy with mandatory legal citation."""

    strategy: str
    estimated_saving_npr: float = Field(ge=0)
    citation: str  # e.g. "Income Tax Act 2058, Section 12, Clause 1"


class AllocationSplit(BaseModel):
    """Recommended portfolio allocation with rationale."""

    land_pct: float = Field(ge=0, le=100)
    shares_pct: float = Field(ge=0, le=100)
    cash_pct: float = Field(ge=0, le=100)
    rationale: str


class AssetRebalance(BaseModel):
    """Rebalancing recommendation: current vs recommended."""

    current: PortfolioSplit
    recommended: AllocationSplit
    urgency: Literal["low", "medium", "high"]


class TradeAdvisory(BaseModel):
    """Swing trade recommendation (1–6 month horizon). Advisory only."""

    ticker: str
    direction: Literal["buy", "sell", "hold"]
    entry_zone: str
    exit_zone: str
    timeframe: str
    thesis: str
    global_trend_link: str


class InvestmentThesis(BaseModel):
    """Long-term (3–5+ year) investment thesis for Nepal markets."""

    sector: str
    companies: list[str]
    horizon: str
    thesis: str
    govt_incentives: str
    legal_risks: str
