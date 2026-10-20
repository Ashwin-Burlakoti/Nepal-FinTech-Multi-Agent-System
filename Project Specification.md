# Project Specification: Nepal FinTech Multi-Agent System

## 1. Tech Stack (Pure Python Web + Mobile)
- **Frontend (Web + iOS/Android):** Flet (Python wrapper for Flutter)
- **Backend & API:** FastAPI + Pydantic v2 (strict JSON output validation)
- **Agent Orchestration:** LangGraph or CrewAI / LiteLLM
- **Database & RAG:** SQLite (user portfolio, notifications) + ChromaDB (Nepal Tax Acts, KVDA plans, NEPSE filings)
- **Scheduler:** APScheduler (low-frequency data ingestion & alert triggers)

## 2. Core Design Pattern: The Triad Debate Engine
Do NOT duplicate agent orchestration logic. Implement a single `BaseTriadAgent` class:
1. `StrategicThinker`: Drafts initial thesis using RAG + Market Analyzer context.
2. `Critique`: Red-teams thesis for macro risks, regulatory traps, or legal non-compliance.
3. `Judge`: Weighs both arguments, rejects unverified claims, and emits a validated Pydantic `NotificationPayload`.

## 3. Agent Modules & Boundaries
- **`MarketAnalyzer` (Source Hub):** Scrapes/ingests global macro (US M2, bond yields, Japan/China/India/US policies, NASDAQ/Nikkei/SGX, oil/gold/energy supply chains, defense/AI/oil giants) + Nepal local data (NRB metrics, NEPSE, KVDA town planning like Dukuchhap). Maps global spillover to Nepal. Outputs a unified `MacroState` JSON.
- **`TaxPlanner`:** Input: User income sources. Retrieval: Nepal Income Tax Act 2058 & Cooperative Tax policies via ChromaDB. Output: Legal tax-saving strategies with mandatory `[Act, Section, Clause]` citations.
- **`AssetManager`:** Input: Current portfolio percentages + user risk tolerance + `MacroState`. Output: Custom vs. Recommended allocation split and rebalancing alerts (e.g., trimming 80% land concentration into equities/cash).
- **`TraderAgent`:** Input: `MacroState` + NEPSE company financials + sentiment + global-to-local trend lag (e.g., EV adoption). Output: 1–6 month swing trade suggestions with entry/exit zones (advisory only).
- **`InvestorAgent`:** Input: `MacroState` + multi-year fundamentals + legal/compliance screening + government sector incentives. Output: 3–5+ year compounding investment theses.

## 4. Data & Notification Schema
Every recommendation saves to `notifications` table:
- `id`, `agent_type`, `short_title` (<= 60 chars), `action_summary`, `thinker_points`, `critique_risks`, `judge_verdict`, `citations` (list of URLs/Act sections), `created_at`, `is_read`.

## 5. Security & Code Quality Rules
- Zero hardcoded API keys; use `pydantic-settings` with `.env`.
- Encrypt user income/asset tables at rest.
- Max 200 lines per Python file; enforce strict type hints and modular imports.