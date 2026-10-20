# Nepal FinTech Multi-Agent System

An AI-powered Wealth & Tax Advisory Multi-Agent System tailored specifically for Nepal's economic, financial, and legal landscape. Built in 100% pure Python with a cross-platform Web & Mobile interface (Flet / Flutter), FastAPI backend, SQLite encrypted storage, ChromaDB vector RAG, and an autonomous Triad Debate Engine.

---

## 🏛️ Core Design Pattern: The Triad Debate Engine

All agents in the system inherit from `BaseTriadAgent` to enforce rigorous compliance and eliminate hallucinations. Every recommendation passes through a three-stage internal debate before emitting a validated decision:

1. **StrategicThinker**: Proposes strategy, allocations, or tax optimization based on user profile and macroeconomic indicators.
2. **Critique**: Red-teams the thesis for macro risks, liquidity constraints, NRB regulations, Inland Revenue Department (IRD) audit exposure, or legal compliance.
3. **Judge**: Weighs arguments from both sides, rejects unverified assertions, enforces mandatory source citations (`[Act, Section, Clause]` or regulatory gazettes), and produces a structured `NotificationPayload`.

```
[ User Profile / Macro State / RAG ]
                │
                ▼
      ┌──────────────────┐
      │ StrategicThinker │ ──► Proposes initial thesis
      └──────────────────┘
                │
                ▼
      ┌──────────────────┐
      │     Critique     │ ──► Challenges risks, compliance & liquidity
      └──────────────────┘
                │
                ▼
      ┌──────────────────┐
      │      Judge       │ ──► Enforces citations & emits NotificationPayload
      └──────────────────┘
```

---

## 🤖 Specialized Agents

| Agent | Scope & Functionality | Citations / Data Sources |
|---|---|---|
| **MarketAnalyzer** | Central source hub. Tracks global macro trends (US M2/yields, China/India policies, commodities) and local Nepal indicators (GDP, NEPSE, NRB policies, land prices). Maps global spillover into a unified `MacroState`. | NRB directives, global macro feeds, NEPSE |
| **TaxPlanner** | Personal tax optimization for Nepal income sources (salary, business, rental, capital gains). Queries Nepal tax laws to suggest legal tax reduction. | Nepal Income Tax Act 2058, Cooperative Act 2074 |
| **AssetManager** | Rebalancing advisory comparing current allocations against recommended splits across Nepal land, shares (NEPSE), and cash. | NRB rates, market cycles, risk tolerance |
| **Trader** | Low-frequency swing trade advisory (1–6 month horizon) identifying entry/exit zones and sector rotations. Advisory only. | NEPSE filings, company financials, SEBON rules |
| **Investor** | 3–5+ year long-term compounding theses across key Nepal growth sectors (hydropower, banking, tourism). | Fundamentals, corporate incentives, legal risks |

---

## 📡 Live Ingestion & Automated Retention Pruning

1. **NEPSE Filings Continuous Sync**:
   - Background worker periodically polls for live corporate disclosures, dividend announcements, right shares, and quarterly reports.
   - Embeds filings into ChromaDB with company ticker, year, and category metadata.
2. **Government Land Planning Ingestion**:
   - Continuously monitors government gazettes, KVDA town planning notices, and infrastructure development decisions.
3. **Automated Lifecycle / Pruning (TTL)**:
   - Filings and notices older than **8–10 years** are automatically pruned from vector storage by scheduled retention jobs, keeping advisory intelligence fresh and relevant.

---

## 🔒 Security & Guardrails

- **Zero Hardcoded Secrets**: Configuration is strictly managed through `.env` using `pydantic-settings`.
- **Field-Level Encryption at Rest**: Sensitive financial records (user income sources, portfolio allocations) are encrypted using cryptography (Fernet) before writing to SQLite.
- **Citation Guardrail**: Any agent verdict lacking specific legal or market citations is automatically rejected.
- **Modular Codebase**: Every Python file in the codebase is strictly maintained under 200 lines.

---

## 📁 Repository Structure

```
Nepal-FinTech-Multi-Agent-System/
├── src/nepal_fintech/
│   ├── agents/               # 5 Triad-based specialized agents
│   │   ├── market_analyzer.py
│   │   ├── tax_planner.py
│   │   ├── asset_manager.py
│   │   ├── trader.py
│   │   └── investor.py
│   ├── api/                  # FastAPI routers (users, agents, notifications)
│   ├── db/                   # Async SQLite engine, ORM models, encrypted CRUD
│   ├── engine/               # LLM connector, Triad debate engine, Pydantic schemas
│   ├── rag/                  # ChromaDB store, ingestion, retriever, live monitors
│   │   ├── store.py
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── monitors.py       # NEPSE/Land live monitoring & retention pruner
│   ├── scheduler/            # APScheduler background sync & cleanup jobs
│   ├── ui/                   # Flet Cross-Platform Web & Mobile UI
│   │   ├── onboarding.py     # Multi-income profile onboarding form
│   │   ├── dashboard.py      # Macro view and agent execution panel
│   │   └── notifications.py  # Expandable debate & citation drawer
│   ├── config.py             # Pydantic Settings
│   ├── encryption.py         # Fernet encryption helpers
│   └── main.py               # Application factory & CLI runner
├── data/rag_docs/            # Authentic legal reference documents
│   ├── income_tax_act_2058.txt
│   └── cooperative_tax_act.txt
├── tests/                    # Comprehensive unit and integration test suite
├── pyproject.toml
└── .env.example
```

---

## 🚀 Quickstart

### 1. Installation

Using `uv` (recommended):

```bash
git clone https://github.com/Ashwin-Burlakoti/Nepal-FinTech-Multi-Agent-System.git
cd Nepal-FinTech-Multi-Agent-System
uv sync
```

### 2. Configuration

Create your `.env` file from the template:

```bash
cp .env.example .env
```

Generate an encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste the generated key into `ENCRYPTION_KEY` in `.env`, along with your `LLM_API_KEY`.

### 3. Launching the System

You can run the application via the CLI:

- **Run FastAPI Backend Only**:
  ```bash
  uv run nepal-fintech api
  # or: uv run python -m nepal_fintech api
  ```
  API documentation is available at `http://localhost:8000/docs`.

- **Run Flet Web & Mobile UI**:
  ```bash
  uv run nepal-fintech ui
  # or: uv run python -m nepal_fintech ui
  ```

- **Run Both Simultaneously**:
  ```bash
  uv run nepal-fintech all
  ```

### 4. Running Tests

Execute the full test suite with pytest:

```bash
uv run pytest -v
```
