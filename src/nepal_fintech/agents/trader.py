"""Trader: Swing trade advisory (1–6 month) for Nepal NEPSE market."""

from __future__ import annotations

from nepal_fintech.engine.triad import BaseTriadAgent


class Trader(BaseTriadAgent):
    """Low-frequency swing trade advisory using macro + company fundamentals.

    Maps global-to-Nepal trend lag (e.g., global EV rise → Nepal EV import boom).
    Advisory only — no auto-execution.
    """

    agent_type: str = "trader"

    def thinker_system_prompt(self) -> str:
        return (
            "You are a StrategicThinker for Nepal NEPSE swing trades.\n"
            "Using macro state, company financials, news sentiment, and "
            "government sector policies:\n"
            "1. Identify 1–6 month swing trade opportunities on NEPSE\n"
            "2. Map global-to-Nepal trend lags (e.g., global EV rise → "
            "Nepal EV import/distribution boom → related NEPSE stocks)\n"
            "3. Analyze sector rotation opportunities\n"
            "4. Provide specific entry and exit price zones\n"
            "5. Consider NEPSE circuit breaker rules and liquidity\n\n"
            "Output JSON with keys: thesis, key_points (list), data_sources (list)."
        )

    def critique_system_prompt(self) -> str:
        return (
            "You are a Critique analyst for Nepal swing trade ideas.\n"
            "Challenge each trade thesis for:\n"
            "1. NEPSE liquidity — can this trade actually be executed?\n"
            "2. Global-to-Nepal lag assumption validity\n"
            "3. Company-specific risks (governance, financials quality)\n"
            "4. Regulatory risks (SEBON rules, promoter share locks)\n"
            "5. Exit risk — what if the stock becomes illiquid at exit?\n"
            "6. Overfit to recent news without fundamental backing\n\n"
            "Output JSON with keys: objections (list), risk_flags (list), "
            "compliance_issues (list)."
        )

    def judge_system_prompt(self) -> str:
        return (
            "You are the Judge for Nepal swing trade advisory.\n"
            "Synthesize trade thesis and critique objections.\n"
            "Only approve trades with:\n"
            "1. Clear fundamental or technical thesis\n"
            "2. Defined entry/exit zones with risk-reward > 2:1\n"
            "3. Adequate NEPSE liquidity for execution\n"
            "4. Explicit disclaimer: ADVISORY ONLY, not financial advice\n\n"
            "Output JSON with keys: decision (str), confidence (low/medium/high), "
            "action_items (list), citations (list — REQUIRED, include data sources "
            "and any SEBON/regulatory references)."
        )

    def build_user_prompt(self, context: dict) -> str:
        macro = context.get("macro_state", "No macro data")
        parts = [
            f"Macro State:\n{macro}",
            f"\nSector Focus: {context.get('sector', 'All sectors')}",
            f"\nCompany Financials:\n{context.get('financials', 'N/A')}",
            f"\nRecent News/Sentiment:\n{context.get('news', 'N/A')}",
            f"\nGovernment Policies:\n{context.get('govt_policies', 'N/A')}",
            "\nIdentify swing trade opportunities (1–6 months) with "
            "entry/exit zones. Advisory only.",
        ]
        return "\n".join(parts)
