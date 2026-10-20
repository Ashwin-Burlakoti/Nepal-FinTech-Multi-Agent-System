"""TaxPlanner: Legal tax optimization using Nepal Income Tax Act via RAG."""

from __future__ import annotations

from nepal_fintech.engine.triad import BaseTriadAgent
from nepal_fintech.rag.retriever import retrieve_with_context


class TaxPlanner(BaseTriadAgent):
    """Suggests legal tax reduction strategies with exact Act/Section citations.

    Queries ChromaDB for Nepal Income Tax Act 2058 and Cooperative Tax policies.
    Never suggests fraud — only legal optimization.
    """

    agent_type: str = "tax_planner"

    def thinker_system_prompt(self) -> str:
        return (
            "You are a StrategicThinker for Nepal tax optimization.\n"
            "Using the provided tax law context and user income profile:\n"
            "1. Identify legal tax-saving strategies under Nepal Income Tax Act 2058\n"
            "2. Consider cooperative tax benefits if applicable\n"
            "3. Evaluate deductions, exemptions, and allowances\n"
            "4. Consider income restructuring (e.g., leasing home to business)\n\n"
            "CRITICAL: Every strategy MUST cite the exact Act, Section, and Clause.\n"
            "Never suggest anything that constitutes tax fraud or evasion.\n\n"
            "Output JSON with keys: thesis, key_points (list), data_sources (list)."
        )

    def critique_system_prompt(self) -> str:
        return (
            "You are a Critique analyst for Nepal tax strategies.\n"
            "Challenge each proposed strategy for:\n"
            "1. Legal compliance — does the cited section actually support this?\n"
            "2. IRD (Inland Revenue Department) audit risk\n"
            "3. Recent amendments that may have changed the rules\n"
            "4. Anti-avoidance provisions in the Act\n"
            "5. Documentation requirements the user might fail to meet\n\n"
            "Output JSON with keys: objections (list), risk_flags (list), "
            "compliance_issues (list)."
        )

    def judge_system_prompt(self) -> str:
        return (
            "You are the Judge for Nepal tax optimization advice.\n"
            "Synthesize the Thinker's strategies and Critique's objections.\n"
            "ONLY approve strategies that:\n"
            "1. Have valid, specific legal citations (Act, Section, Clause)\n"
            "2. Are clearly legal (not tax evasion)\n"
            "3. Have manageable audit risk\n\n"
            "Reject any strategy lacking a proper citation.\n\n"
            "Output JSON with keys: decision (str), confidence (low/medium/high), "
            "action_items (list), citations (list — REQUIRED, must include "
            "Act/Section/Clause references)."
        )

    def build_user_prompt(self, context: dict) -> str:
        # Retrieve relevant tax law context from ChromaDB
        income_desc = context.get("income_description", "")
        rag_context = retrieve_with_context(
            query=f"tax optimization for {income_desc}",
            collection_name="tax_acts",
            n_results=8,
        )
        parts = [
            "User income profile:",
            str(context.get("income_sources", [])),
            f"\nTotal annual income (NPR): {context.get('total_income', 'N/A')}",
            f"\nRisk profile: {context.get('risk_profile', 'moderate')}",
            f"\n\nRelevant Nepal Tax Law Context:\n{rag_context}",
            "\n\nSuggest legal tax-saving strategies with exact citations.",
        ]
        return "\n".join(parts)
