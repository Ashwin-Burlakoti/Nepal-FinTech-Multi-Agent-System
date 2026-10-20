"""Specialized triad agents for Nepal FinTech Advisory."""

from __future__ import annotations

from nepal_fintech.agents.asset_manager import AssetManager
from nepal_fintech.agents.investor import Investor
from nepal_fintech.agents.market_analyzer import MarketAnalyzer
from nepal_fintech.agents.tax_planner import TaxPlanner
from nepal_fintech.agents.trader import Trader

__all__ = [
    "AssetManager",
    "Investor",
    "MarketAnalyzer",
    "TaxPlanner",
    "Trader",
]
