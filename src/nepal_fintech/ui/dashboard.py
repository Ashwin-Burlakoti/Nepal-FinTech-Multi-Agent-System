"""Dashboard view — macro state card and agent action buttons."""

from __future__ import annotations

import flet as ft
import httpx

from nepal_fintech.ui.constants import API_BASE
from nepal_fintech.ui.notifications import NotificationDrawer


class DashboardView:
    """Main dashboard: shows macro snapshot and lets user trigger agents."""

    def __init__(
        self,
        page: ft.Page,
        state: dict,
        notif_drawer: NotificationDrawer,
    ) -> None:
        self.page = page
        self.state = state
        self.notif_drawer = notif_drawer
        self.macro_text = ft.Text("Loading macro state...", selectable=True)
        self.status_text = ft.Text("")

    def _load_macro(self) -> None:
        """Fetch latest macro state from API."""
        try:
            resp = httpx.get(f"{API_BASE}/agents/macro/latest", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                spill = data.get("spillover_analysis", "N/A")
                self.macro_text.value = f"Spillover: {spill[:200]}..."
            else:
                self.macro_text.value = "No macro data yet — run MarketAnalyzer first."
        except Exception as exc:
            self.macro_text.value = f"Error loading macro: {exc}"

    def _run_agent(self, agent_name: str) -> None:
        """Trigger an agent run via API."""
        self.status_text.value = f"Running {agent_name}..."
        self.page.update()
        user_id = self.state.get("user_id", 1)
        try:
            resp = httpx.post(
                f"{API_BASE}/agents/run/{agent_name}",
                json={"context_note": "User-triggered run"},
                params={"user_id": user_id},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            title = data["payload"]["short_title"]
            self.status_text.value = f"✅ {agent_name}: {title}"
            self.notif_drawer.refresh()
        except Exception as exc:
            self.status_text.value = f"❌ {agent_name} error: {exc}"
        self.page.update()

    def _make_agent_button(self, label: str, agent_name: str) -> ft.FilledButton:
        return ft.FilledButton(
            label,
            on_click=lambda _: self._run_agent(agent_name),
            width=360,
        )

    def _open_notifications(self, e: ft.ControlEvent) -> None:
        self.notif_drawer.refresh()
        self.page.end_drawer.open = True
        self.page.update()

    def build(self) -> ft.View:
        self._load_macro()
        return ft.View(
            route="/dashboard",
            controls=[
                ft.AppBar(
                    title=ft.Text("Nepal FinTech Dashboard"),
                    actions=[
                        ft.IconButton(
                            ft.Icons.NOTIFICATIONS,
                            on_click=self._open_notifications,
                            tooltip="Notifications",
                        ),
                    ],
                ),
                ft.Column(
                    [
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Macro State", size=18, weight=ft.FontWeight.BOLD),
                                    self.macro_text,
                                    ft.TextButton(
                                        "Refresh",
                                        on_click=lambda _: (self._load_macro(), self.page.update()),
                                    ),
                                ]),
                                padding=16,
                            ),
                        ),
                        ft.Divider(),
                        ft.Text("Run Agents", size=18, weight=ft.FontWeight.BOLD),
                        self._make_agent_button("📊 Market Analyzer", "market_analyzer"),
                        self._make_agent_button("🧾 Tax Planner", "tax_planner"),
                        self._make_agent_button("💰 Asset Manager", "asset_manager"),
                        self._make_agent_button("📈 Trader (Swing)", "trader"),
                        self._make_agent_button("🏦 Investor (Long-term)", "investor"),
                        ft.Divider(),
                        self.status_text,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
            ],
        )
