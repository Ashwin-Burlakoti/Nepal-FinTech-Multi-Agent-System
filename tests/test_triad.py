"""Tests for the Triad Debate Engine pattern (Thinker -> Critique -> Judge)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
import pytest

from nepal_fintech.agents.tax_planner import TaxPlanner
from nepal_fintech.engine.schemas import NotificationPayload


@pytest.mark.asyncio
async def test_triad_debate_pipeline_success() -> None:
    agent = TaxPlanner()

    mock_thinker_response = {
        "thesis": "Utilize Section 12 life insurance and retirement deductions",
        "key_points": ["Save up to NPR 300,000 via CIT/SSF", "Save NPR 40,000 via insurance"],
        "data_sources": ["Income Tax Act 2058, Section 12"],
    }
    mock_critique_response = {
        "objections": ["Requires policy receipt within current fiscal year"],
        "risk_flags": ["Audit compliance"],
        "compliance_issues": [],
    }
    mock_judge_response = {
        "decision": "Contribute maximum permissible to SSF and purchase approved health insurance",
        "confidence": "high",
        "action_items": ["Transfer NPR 300,000 to SSF", "Submit receipts before Ashadh"],
        "citations": ["Income Tax Act 2058, Section 12, Clause 1"],
    }

    with patch(
        "nepal_fintech.engine.triad.chat_json",
        side_effect=[
            mock_thinker_response,
            mock_critique_response,
            mock_judge_response,
        ],
    ):
        context = {
            "income_sources": [{"source_type": "salary", "annual_amount_npr": 1500000}],
            "total_income": 1500000,
            "risk_profile": "moderate",
        }
        payload = await agent.run(context)

        assert isinstance(payload, NotificationPayload)
        assert payload.agent_type == "tax_planner"
        assert len(payload.short_title) <= 60
        assert len(payload.judge_verdict.citations) >= 1
        assert "Income Tax Act 2058" in payload.judge_verdict.citations[0]


@pytest.mark.asyncio
async def test_triad_rejects_judge_without_citations() -> None:
    agent = TaxPlanner()

    mock_thinker = {
        "thesis": "Tax plan thesis",
        "key_points": ["Point 1"],
        "data_sources": ["Doc 1"],
    }
    mock_critique = {
        "objections": ["Objection 1"],
        "risk_flags": [],
        "compliance_issues": [],
    }
    mock_judge_no_citations = {
        "decision": "Unsupported recommendation without citations",
        "confidence": "low",
        "action_items": ["Action 1"],
        "citations": [],  # Violates required citations rule
    }

    with patch(
        "nepal_fintech.engine.triad.chat_json",
        side_effect=[mock_thinker, mock_critique, mock_judge_no_citations],
    ):
        with pytest.raises(Exception):  # Either Pydantic ValidationError or ValueError
            await agent.run({})
