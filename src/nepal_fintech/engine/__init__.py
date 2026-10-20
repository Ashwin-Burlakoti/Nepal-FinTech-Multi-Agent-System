"""Core engine modules: LLM connector, triad debate engine, and schemas."""

from __future__ import annotations

from nepal_fintech.engine.llm import chat, chat_json
from nepal_fintech.engine.schemas import (
    CritiqueOutput,
    IncomeSource,
    JudgeVerdict,
    MacroState,
    NotificationPayload,
    PortfolioSplit,
    ThinkerOutput,
    UserProfile,
)
from nepal_fintech.engine.triad import BaseTriadAgent

__all__ = [
    "BaseTriadAgent",
    "CritiqueOutput",
    "IncomeSource",
    "JudgeVerdict",
    "MacroState",
    "NotificationPayload",
    "PortfolioSplit",
    "ThinkerOutput",
    "UserProfile",
    "chat",
    "chat_json",
]
