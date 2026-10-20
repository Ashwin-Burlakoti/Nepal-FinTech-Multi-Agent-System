"""Agent execution API routes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nepal_fintech.agents.asset_manager import AssetManager
from nepal_fintech.agents.investor import Investor
from nepal_fintech.agents.market_analyzer import MarketAnalyzer
from nepal_fintech.agents.tax_planner import TaxPlanner
from nepal_fintech.agents.trader import Trader
from nepal_fintech.db.crud import (
    get_latest_macro_state,
    get_user,
    save_macro_state,
    save_notification,
)
from nepal_fintech.db.engine import get_session
from nepal_fintech.engine.schemas import GlobalMacro, MacroState, NepalLocal

router = APIRouter(prefix="/api/agents", tags=["agents"])

AgentName = Literal[
    "market_analyzer", "tax_planner", "asset_manager", "trader", "investor"
]

AGENT_MAP: dict[str, type] = {
    "market_analyzer": MarketAnalyzer,
    "tax_planner": TaxPlanner,
    "asset_manager": AssetManager,
    "trader": Trader,
    "investor": Investor,
}


@router.post("/run/{agent_name}")
async def run_agent(
    agent_name: AgentName,
    context: dict,
    user_id: int = 1,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Run a specific agent's triad pipeline and save the notification."""
    agent_cls = AGENT_MAP.get(agent_name)
    if agent_cls is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    # Inject macro state for agents that need it
    if agent_name != "market_analyzer":
        macro_json = await get_latest_macro_state(session)
        if macro_json:
            context.setdefault("macro_state", macro_json)

    # Inject user data for personalized agents
    if agent_name in ("tax_planner", "asset_manager"):
        user = await get_user(session, user_id)
        if user:
            context.setdefault("income_sources", user.get("income_sources"))
            context.setdefault("portfolio_split", user.get("portfolio_split"))
            context.setdefault("risk_profile", user.get("risk_profile"))

    agent = agent_cls()
    try:
        payload = await agent.run(context)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Save notification
    notif_id = await save_notification(session, user_id, payload)

    # If MarketAnalyzer, cache structured MacroState
    if agent_name == "market_analyzer":
        macro_state = MacroState(
            global_macro=GlobalMacro(
                us_m2_trend="US M2 trend monitored",
                us_bond_yields="US 10-year Treasury yield dynamics",
                japan_policy="BOJ rate posture",
                china_policy="PBOC easing and bilateral trade",
                india_policy="RBI monetary policy & INR-NPR peg",
                nasdaq="Tech sentiment",
                nikkei="Asian market trend",
                sgx="Regional liquidity indicator",
                oil_gold_energy="Global commodity & energy supply lines",
                defense_ai_sector="Strategic supply chain shifts",
                geopolitical_risks="Regional trade & transit routes",
            ),
            nepal_local=NepalLocal(
                gdp_trend="Nepal GDP & remittance liquidity",
                nepse_status="NEPSE liquidity & sector rotation",
                nrb_policy="NRB monetary directives & interest rates",
                kvda_updates="KVDA town planning (Dukuchhap & outer urban zones)",
                land_price_trend="Kathmandu valley & suburban land valuation",
            ),
            spillover_analysis=payload.action_summary,
            timestamp=datetime.now(timezone.utc),
        )
        await save_macro_state(session, macro_state.model_dump_json())

    return {
        "notification_id": notif_id,
        "payload": payload.model_dump(),
    }


@router.get("/macro/latest")
async def get_macro(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get the latest cached macro state."""
    macro_json = await get_latest_macro_state(session)
    if macro_json is None:
        raise HTTPException(status_code=404, detail="No macro state cached yet")
    return json.loads(macro_json)
