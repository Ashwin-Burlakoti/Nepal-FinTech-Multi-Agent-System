"""MarketAnalyzer: Central intelligence hub for global + Nepal macro data."""

from __future__ import annotations

from nepal_fintech.engine.triad import BaseTriadAgent


class MarketAnalyzer(BaseTriadAgent):
    """Tracks global macro and Nepal-local data, maps spillover effects.

    All actionable investments are strictly limited to Nepal.
    Foreign markets are used only as risk indicators.
    """

    agent_type: str = "market_analyzer"

    def thinker_system_prompt(self) -> str:
        return (
            "You are a StrategicThinker for Nepal macro-economic analysis.\n"
            "Analyze the provided global and Nepal data to identify:\n"
            "1. Key global macro trends (US M2/bonds, Japan/China/India policy, "
            "NASDAQ/Nikkei/SGX, oil/gold/energy supply chains, AI/defense sectors)\n"
            "2. Nepal-local indicators (GDP, NEPSE, NRB policy, KVDA town planning "
            "like Dukuchhap, land prices)\n"
            "3. How global trends spill over to Nepal markets\n\n"
            "Output JSON with keys: thesis, key_points (list), data_sources (list).\n"
            "Focus on actionable Nepal implications only."
        )

    def critique_system_prompt(self) -> str:
        return (
            "You are a Critique analyst challenging a Nepal macro thesis.\n"
            "Red-team the analysis for:\n"
            "1. Over-reliance on global correlation without Nepal-specific evidence\n"
            "2. Ignoring NRB monetary policy lag or capital controls\n"
            "3. Missing geopolitical risks (India trade dependency, China belt-road)\n"
            "4. NEPSE illiquidity and circuit-breaker risks\n"
            "5. KVDA/land regulatory changes\n\n"
            "Output JSON with keys: objections (list), risk_flags (list), "
            "compliance_issues (list)."
        )

    def judge_system_prompt(self) -> str:
        return (
            "You are the Judge synthesizing Nepal macro analysis.\n"
            "Weigh the Thinker's thesis against the Critique's objections.\n"
            "Produce a balanced final macro state assessment.\n"
            "Reject any claim that lacks a data source.\n\n"
            "Output JSON with keys: decision (str), confidence (low/medium/high), "
            "action_items (list), citations (list of data sources — REQUIRED, "
            "cannot be empty)."
        )

    def build_user_prompt(self, context: dict) -> str:
        parts = ["Analyze the following market data for Nepal implications:\n"]
        if "global_data" in context:
            parts.append(f"Global Data:\n{context['global_data']}\n")
        if "nepal_data" in context:
            parts.append(f"Nepal Data:\n{context['nepal_data']}\n")
        if "news" in context:
            parts.append(f"Recent News:\n{context['news']}\n")
        parts.append(
            "Provide a comprehensive macro state analysis with "
            "global-to-Nepal spillover mapping."
        )
        return "\n".join(parts)
