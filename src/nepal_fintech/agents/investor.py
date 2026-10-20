"""Investor: Long-term (3–5+ year) investment advisory for Nepal."""

from __future__ import annotations

from nepal_fintech.engine.triad import BaseTriadAgent


class Investor(BaseTriadAgent):
    """Evaluates fundamentals, sector growth, and legal risks for
    long-term Nepal investments with 3–5+ year compounding thesis.
    """

    agent_type: str = "investor"

    def thinker_system_prompt(self) -> str:
        return (
            "You are a StrategicThinker for long-term Nepal investments.\n"
            "Evaluate for 3–5+ year investment horizons:\n"
            "1. Sector growth trajectories in Nepal (hydropower, banking, "
            "insurance, manufacturing, tourism, fintech)\n"
            "2. Company fundamentals: ROE, debt ratios, earnings growth\n"
            "3. Government tax incentives and corporate subsidies\n"
            "4. Infrastructure development catalysts (KVDA, road projects)\n"
            "5. Demographic trends supporting long-term demand\n"
            "6. Regulatory moats and barriers to entry\n\n"
            "Output JSON with keys: thesis, key_points (list), data_sources (list)."
        )

    def critique_system_prompt(self) -> str:
        return (
            "You are a Critique analyst for long-term Nepal investments.\n"
            "Challenge the investment thesis for:\n"
            "1. Political instability risk (government changes, policy reversals)\n"
            "2. Regulatory risk (SEBON rule changes, NRB directives)\n"
            "3. Corporate governance quality of Nepal companies\n"
            "4. Currency depreciation (NPR vs USD) impact on real returns\n"
            "5. Concentration risk in Nepal's small market\n"
            "6. Exit liquidity for long-term positions\n"
            "7. Environmental and social governance gaps\n\n"
            "Output JSON with keys: objections (list), risk_flags (list), "
            "compliance_issues (list)."
        )

    def judge_system_prompt(self) -> str:
        return (
            "You are the Judge for long-term Nepal investment theses.\n"
            "Synthesize the thesis and critique into a final verdict.\n"
            "Only approve investments with:\n"
            "1. Strong multi-year fundamental case\n"
            "2. Identified government/regulatory tailwinds\n"
            "3. Acceptable governance and compliance standards\n"
            "4. Realistic exit strategy given NEPSE liquidity\n\n"
            "Output JSON with keys: decision (str), confidence (low/medium/high), "
            "action_items (list), citations (list — REQUIRED, include fundamental "
            "data sources and legal/regulatory references)."
        )

    def build_user_prompt(self, context: dict) -> str:
        macro = context.get("macro_state", "No macro data")
        parts = [
            f"Macro State:\n{macro}",
            f"\nSector of Interest: {context.get('sector', 'All sectors')}",
            f"\nCompany Fundamentals:\n{context.get('fundamentals', 'N/A')}",
            f"\nGovernment Incentives:\n{context.get('govt_incentives', 'N/A')}",
            f"\nLegal/Compliance Notes:\n{context.get('legal_notes', 'N/A')}",
            f"\nInvestment Horizon: {context.get('horizon', '3-5 years')}",
            "\nProvide a long-term investment thesis with sector and "
            "company recommendations.",
        ]
        return "\n".join(parts)
