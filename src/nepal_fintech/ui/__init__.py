"""Flet Web & Mobile UI views and components."""

from __future__ import annotations

from nepal_fintech.ui.app import main, start_ui
from nepal_fintech.ui.constants import API_BASE
from nepal_fintech.ui.dashboard import DashboardView
from nepal_fintech.ui.notifications import NotificationDrawer
from nepal_fintech.ui.onboarding import OnboardingView

__all__ = [
    "API_BASE",
    "DashboardView",
    "NotificationDrawer",
    "OnboardingView",
    "main",
    "start_ui",
]
