"""BaseTriadAgent: Reusable Thinker → Critique → Judge pipeline (DRY)."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from nepal_fintech.engine.llm import chat_json
from nepal_fintech.engine.schemas import (
    CritiqueOutput,
    JudgeVerdict,
    NotificationPayload,
    ThinkerOutput,
)

logger = logging.getLogger(__name__)


class BaseTriadAgent(ABC):
    """Abstract base for all agents. Subclasses define prompts; triad runs the pipeline."""

    agent_type: str = "base"

    # ── Subclass hooks (override these) ──────────────────────────

    @abstractmethod
    def thinker_system_prompt(self) -> str:
        """System prompt for the StrategicThinker step."""

    @abstractmethod
    def critique_system_prompt(self) -> str:
        """System prompt for the Critique step."""

    @abstractmethod
    def judge_system_prompt(self) -> str:
        """System prompt for the Judge step."""

    @abstractmethod
    def build_user_prompt(self, context: dict) -> str:
        """Build the user prompt from the input context dict."""

    # ── Triad Pipeline (DO NOT override) ─────────────────────────

    async def _run_thinker(self, user_prompt: str) -> ThinkerOutput:
        """Step 1: Strategic Thinker proposes a thesis."""
        raw = await chat_json(self.thinker_system_prompt(), user_prompt)
        return ThinkerOutput.model_validate(raw)

    async def _run_critique(
        self, user_prompt: str, thinker: ThinkerOutput
    ) -> CritiqueOutput:
        """Step 2: Critique red-teams the thinker's thesis."""
        critique_input = (
            f"Original context:\n{user_prompt}\n\n"
            f"Thinker's thesis:\n{thinker.model_dump_json(indent=2)}"
        )
        raw = await chat_json(self.critique_system_prompt(), critique_input)
        return CritiqueOutput.model_validate(raw)

    async def _run_judge(
        self,
        user_prompt: str,
        thinker: ThinkerOutput,
        critique: CritiqueOutput,
    ) -> JudgeVerdict:
        """Step 3: Judge synthesizes both into a final verdict."""
        judge_input = (
            f"Original context:\n{user_prompt}\n\n"
            f"Thinker's thesis:\n{thinker.model_dump_json(indent=2)}\n\n"
            f"Critique's objections:\n{critique.model_dump_json(indent=2)}"
        )
        raw = await chat_json(self.judge_system_prompt(), judge_input)
        verdict = JudgeVerdict.model_validate(raw)
        # GUARDRAIL: Reject verdicts without citations
        if not verdict.citations:
            raise ValueError("Judge verdict rejected: no citations provided")
        return verdict

    async def run(self, context: dict) -> NotificationPayload:
        """Execute the full Thinker → Critique → Judge pipeline."""
        user_prompt = self.build_user_prompt(context)
        logger.info("Agent [%s] starting triad pipeline", self.agent_type)

        thinker = await self._run_thinker(user_prompt)
        logger.info("Agent [%s] thinker complete", self.agent_type)

        critique = await self._run_critique(user_prompt, thinker)
        logger.info("Agent [%s] critique complete", self.agent_type)

        judge = await self._run_judge(user_prompt, thinker, critique)
        logger.info("Agent [%s] judge complete", self.agent_type)

        # Build short title from decision (truncate to 60 chars)
        short_title = judge.decision[:57] + "..." if len(judge.decision) > 60 else judge.decision

        return NotificationPayload(
            agent_type=self.agent_type,
            short_title=short_title,
            action_summary=judge.decision,
            thinker_output=thinker,
            critique_output=critique,
            judge_verdict=judge,
        )
