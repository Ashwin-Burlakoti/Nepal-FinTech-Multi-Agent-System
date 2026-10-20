Build a cross-platform Web & Mobile app in 100% Python (FastAPI + Flet UI + SQLite + ChromaDB + LiteLLM/Pydantic) for a Nepal-focused AI Wealth & Tax Advisory system.

### EXECUTION WORKFLOW (PLAN FIRST, THEN EXECUTE)
1. **Phase 1 (Plan):** Output ONLY the directory tree, SQLite/Pydantic schemas, and a 4-step build plan. Wait for my "GO" before writing app code.
2. **Phase 2 (Core Engine):** Build the DB, RAG pipeline, and reusable `TriadDebateEngine`.
3. **Phase 3 (Agents):** Implement the 5 specialized agents inheriting from `TriadDebateEngine`.
4. **Phase 4 (Flet UI):** Build Onboarding (income/portfolio split), Dashboard, and Expandable Notification Drawer.

### CORE ARCHITECTURE & AGENTS
1. **Reusable `TriadDebateEngine` (DRY Principle):** Every agent MUST run a 3-step internal pipeline before emitting output:
   - `StrategicThinker`: Proposes strategy from data.
   - `Critique`: Challenges assumptions, legal compliance, and macro risks.
   - `Judge`: Synthesizes both into a final decision.
2. **`MarketAnalyzer` (Central Intelligence Hub):** Tracks global macro (US M2/bonds, Japan/global rate flows, NASDAQ/SGX/Nikkei/China, wars, oil/gold/energy supply chains from producer to consumer, mining licenses, environmental laws, AI/Oil/Defense giants, US/India/China policies) and local Nepal data (GDP, NEPSE, KVDA town planning e.g., Dukuchhap, land prices). Maps global spillover onto Nepal. All actionable investments are strictly limited to Nepal (foreign housing/markets used only as risk indicators). Feeds all other agents.
3. **`TaxPlanner`:** Takes user income profile; queries ChromaDB (Nepal Income Tax & Cooperative Tax Acts) to suggest legal tax reduction (never fraud, e.g., leasing home to business). MUST cite exact Act, Article, and Section.
4. **`AssetManager`:** Takes user portfolio split (e.g., 80% land) and risk profile. Uses `MarketAnalyzer` to output Custom vs. Recommended allocation splits and rebalancing alerts across Nepal land, shares, and cash.
5. **`Trader` (Swing Advisory):** Uses `MarketAnalyzer`, company financials, news sentiment, govt sector policies, and global-to-Nepal trend lag (e.g., global EV rise -> Nepal EV import boom) to suggest 1–6+ month low-frequency trades with entry/exit zones. Advisory only; no auto-execution.
6. **`Investor` (Long-Term Advisory):** Evaluates fundamentals, sector growth, govt tax/corporate incentives, and legal risks for 3–5+ year Nepal investments.
7. **Notification UI:** All agent outputs trigger notifications with a `short_title`. Clicking expands the full Judge rationale, Thinker/Critique debate, and clickable source/law citations.

### GUARDRAILS (ANTI-BLOAT & SECURITY)
- Modular code: max 200 lines/file, strict Python type hints, zero dead code or duplicated agent loops.
- Strict Pydantic validation on all LLM responses; reject any tax/market claim lacking a source citation.
- Load secrets via `.env`; encrypt user financial inputs in SQLite.

Start Phase 1 now.