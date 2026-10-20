"""AssetManager: Portfolio allocation and rebalancing advisory for Nepal."""

from __future__ import annotations

from nepal_fintech.engine.triad import BaseTriadAgent


class AssetManager(BaseTriadAgent):
    """Analyzes user portfolio split against macro state and risk profile.

    Outputs custom vs. recommended allocation and rebalancing alerts
    across Nepal land, shares (NEPSE), and cash.
    """

    agent_type: str = "asset_manager"

    def thinker_system_prompt(self) -> str:
        return (
            "You are a StrategicThinker for Nepal asset allocation.\n"
            "Given the user's current portfolio, risk profile, and macro state:\n"
            "1. Evaluate concentration risk (e.g., 80% in land is high risk)\n"
            "2. Propose optimal allocation across: Nepal land, NEPSE shares, cash\n"
            "3. Consider NRB interest rates, NEPSE trends, land price cycles\n"
            "4. Factor in the user's risk tolerance level\n"
            "5. Suggest specific rebalancing steps with urgency\n\n"
            "Output JSON with keys: thesis, key_points (list), data_sources (list)."
        )

    def critique_system_prompt(self) -> str:
        return (
            "You are a Critique analyst for Nepal portfolio rebalancing.\n"
            "Challenge the proposed allocation for:\n"
            "1. Liquidity risk — Nepal land is highly illiquid\n"
            "2. NEPSE market depth — can the user actually execute trades?\n"
            "3. Transaction costs (land registration tax ~5-7%)\n"
            "4. Currency risk and inflation hedging gaps\n"
            "5. Over-diversification for small portfolios\n"
            "6. Tax implications of rebalancing (capital gains)\n\n"
            "Output JSON with keys: objections (list), risk_flags (list), "
            "compliance_issues (list)."
        )

    def judge_system_prompt(self) -> str:
        return (
            "You are the Judge for Nepal asset allocation advice.\n"
            "Synthesize the Thinker's allocation and Critique's concerns.\n"
            "Produce a practical rebalancing plan that:\n"
            "1. Acknowledges Nepal market illiquidity constraints\n"
            "2. Provides both ideal and realistic allocation targets\n"
            "3. Specifies timeline for gradual rebalancing\n\n"
            "Output JSON with keys: decision (str), confidence (low/medium/high), "
            "action_items (list of specific steps), citations (list — REQUIRED, "
            "include data sources for market assumptions)."
        )

    def build_user_prompt(self, context: dict) -> str:
        portfolio = context.get("portfolio_split", {})
        macro = context.get("macro_state", "No macro data available")
        parts = [
            "User Portfolio:",
            f"  Land: {portfolio.get('land_pct', 'N/A')}%",
            f"  Shares: {portfolio.get('shares_pct', 'N/A')}%",
            f"  Cash: {portfolio.get('cash_pct', 'N/A')}%",
            f"\nRisk Profile: {context.get('risk_profile', 'moderate')}",
            f"\nCurrent Macro State:\n{macro}",
            "\nProvide allocation recommendation with rebalancing steps.",
        ]
        return "\n".join(parts)
